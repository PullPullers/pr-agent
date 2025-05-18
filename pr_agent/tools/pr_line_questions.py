import argparse
import copy
from functools import partial

from jinja2 import Environment, StrictUndefined

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.algo.ai_handlers.litellm_ai_handler import LiteLLMAIHandler
from pr_agent.algo.git_patch_processing import (
    decouple_and_convert_to_hunks_with_lines_numbers, extract_hunk_lines_from_patch)
from pr_agent.algo.pr_processing import get_pr_diff, retry_with_fallback_models
from pr_agent.algo.token_handler import TokenHandler
from pr_agent.algo.utils import ModelType
from pr_agent.config_loader import get_settings
from pr_agent.git_providers import get_git_provider
from pr_agent.git_providers.git_provider import get_main_pr_language
from pr_agent.log import get_logger
from pr_agent.servers.help import HelpMessage


class PR_LineQuestions:
    def __init__(self, pr_url: str, args=None, ai_handler: partial[BaseAiHandler,] = LiteLLMAIHandler):
        self.question_str = self.parse_args(args)
        self.git_provider = get_git_provider()(pr_url)
        self.main_pr_language = get_main_pr_language(
            self.git_provider.get_languages(), self.git_provider.get_files()
        )
        self.ai_handler = ai_handler()
        self.ai_handler.main_pr_language = self.main_pr_language

        self.vars = {
            "title": self.git_provider.pr.title,
            "branch": self.git_provider.get_pr_branch(),
            "diff": "",  # empty diff for initial calculation
            "question": self.question_str,
            "full_hunk": "",
            "selected_lines": "",
            "conversation_history": "",  
        }
        self.token_handler = TokenHandler(self.git_provider.pr,
                                          self.vars,
                                          get_settings().pr_line_questions_prompt.system,
                                          get_settings().pr_line_questions_prompt.user)
        self.patches_diff = None
        self.prediction = None
        
        # get settings for use conversation history
        self.use_conversation_history = get_settings().pr_questions.use_conversation_history

    def parse_args(self, args):
        if args and len(args) > 0:
            question_str = " ".join(args)
        else:
            question_str = ""
        return question_str


    async def run(self):
        get_logger().info('Answering a PR lines question...')
        # if get_settings().config.publish_output:
        #     self.git_provider.publish_comment("Preparing answer...", is_temporary=True)

        # set conversation history if enabled
        try:
            if self.use_conversation_history:
                self._load_conversation_history()
            else:
                get_logger().info("Conversation history is disabled.")
        except Exception as e:
            get_logger().warning(f"Failed to load conversation history: {e}")

        self.patch_with_lines = ""
        ask_diff = get_settings().get('ask_diff_hunk', "")
        line_start = get_settings().get('line_start', '')
        line_end = get_settings().get('line_end', '')
        side = get_settings().get('side', 'RIGHT')
        file_name = get_settings().get('file_name', '')
        comment_id = get_settings().get('comment_id', '')
        if ask_diff:
            self.patch_with_lines, self.selected_lines = extract_hunk_lines_from_patch(ask_diff,
                                                                                       file_name,
                                                                                       line_start=line_start,
                                                                                       line_end=line_end,
                                                                                       side=side
                                                                                       )
        else:
            diff_files = self.git_provider.get_diff_files()
            for file in diff_files:
                if file.filename == file_name:
                    self.patch_with_lines, self.selected_lines = extract_hunk_lines_from_patch(file.patch, file.filename,
                                                                                               line_start=line_start,
                                                                                               line_end=line_end,
                                                                                               side=side)
        if self.patch_with_lines:
            model_answer = await retry_with_fallback_models(self._get_prediction, model_type=ModelType.WEAK)
            # sanitize the answer so that no line will start with "/"
            model_answer_sanitized = model_answer.strip().replace("\n/", "\n /")
            if model_answer_sanitized.startswith("/"):
                model_answer_sanitized = " " + model_answer_sanitized

            get_logger().info('Preparing answer...')
            if comment_id:
                self.git_provider.reply_to_comment_from_comment_id(comment_id, model_answer_sanitized)
            else:
                self.git_provider.publish_comment(model_answer_sanitized)

        return ""
        
    def _load_conversation_history(self):
        """generate conversation history from the code review thread"""
        try:
            comment_id = get_settings().get('comment_id', '')
            file_path = get_settings().get('file_name', '')
            line_number = get_settings().get('line_end', '')
            
            # return if no comment id or file path and line number
            if not (comment_id or (file_path and line_number)):
                return

            # initialize conversation history
            conversation_history = []
            
            if hasattr(self.git_provider, 'get_review_thread_comments') and comment_id:
                try:
                    # get review thread comments
                    thread_comments = self.git_provider.get_review_thread_comments(comment_id)
                    
                    # current question id (this question is excluded from the context)
                    current_question_id = comment_id
                    
                    # generate conversation history from the comments
                    for comment in thread_comments:
                        # skip empty comments
                        body = getattr(comment, 'body', '')
                        if not body or not body.strip():
                            continue
                        
                        # except for current question
                        # except for current question
                        if current_question_id and comment.id == current_question_id:
                        
                        # remove the AI command (/ask etc) from the beginning of the comment (optional)
                        clean_body = body
                        if clean_body.startswith('/'):
                            clean_body = clean_body.split('\n', 1)[-1] if '\n' in clean_body else ''
                            
                        if not clean_body.strip():
                            continue
                            
                        # author info
                        user = comment.user
                        author = user.login if hasattr(user, 'login') else 'Unknown'
                        
                        # confirm if the author is the current user (AI vs user)
                        is_ai = 'bot' in author.lower() or '[bot]' in author.lower()
                        role = 'AI' if is_ai else 'User'
                        
                        # append to the conversation history
                        conversation_history.append(f"{role} ({author}): {clean_body}")
                    
                    # transform the conversation history to a string
                    if conversation_history:
                        self.vars["conversation_history"] = "\n\n".join(conversation_history)
                        get_logger().info(f"Loaded {len(conversation_history)} comments from the code review thread")
                    else:
                        self.vars["conversation_history"] = ""
                        
                except Exception as e:
                    get_logger().warning(f"Failed to get review thread comments: {e}")
                    self.vars["conversation_history"] = ""
        
        except Exception as e:
            get_logger().error(f"Error loading conversation history: {e}")
            self.vars["conversation_history"] = ""

    async def _get_prediction(self, model: str):
        variables = copy.deepcopy(self.vars)
        variables["full_hunk"] = self.patch_with_lines  # update diff
        variables["selected_lines"] = self.selected_lines
        environment = Environment(undefined=StrictUndefined)
        system_prompt = environment.from_string(get_settings().pr_line_questions_prompt.system).render(variables)
        user_prompt = environment.from_string(get_settings().pr_line_questions_prompt.user).render(variables)
        if get_settings().config.verbosity_level >= 2:
            # get_logger().info(f"\nSystem prompt:\n{system_prompt}")
            # get_logger().info(f"\nUser prompt:\n{user_prompt}")
            print(f"\nSystem prompt:\n{system_prompt}")
            print(f"\nUser prompt:\n{user_prompt}")

        response, finish_reason = await self.ai_handler.chat_completion(
            model=model, temperature=get_settings().config.temperature, system=system_prompt, user=user_prompt)
        return response
