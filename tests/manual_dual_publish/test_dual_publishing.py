# 예시 1: 불필요한 디버그 출력
print("debug1")
print("debug2")

# 예시 2: try-except 없는 파일 I/O
try:
    f = open("file.txt")  # file.txt가 없어도 에러 안 나게 try-except 처리
    data = f.read()
    f.close()
except:
    pass

# 예시 3: 조건 중복
x = 8
if x > 10:
    print("Big")
elif x > 5:
    print("Medium")

# 예시 4: 하드코딩된 매직넘버
score = 85
if score > 90:
    print("Excellent")

