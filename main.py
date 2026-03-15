import os
import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai

# [1] AI 콘텐츠 생성 (Gemini)
def generate_content():
    genai.configure(api_key=os.environ["AIzaSyDt0DhZuAn_i1jPTkhsjU2ZEz1brbf-qVs"])
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = """
    주제: 'S&P 500 분석' 또는 '현대 물리학의 흥미로운 법칙' 중 하나를 선택.
    조건:
    1. 가독성을 위해 HTML 태그(h2, h3, p)를 사용해 작성할 것.
    2. 전문적인 수치를 포함하되 논리적으로 서술할 것.
    3. 마지막에 '복리의 마법을 믿는 고3의 기록' 문구를 넣을 것.
    """
    response = model.generate_content(prompt)
    return response.text

# [2] 블로그 자동 포스팅 (Playwright)
async def post_to_blog():
    async with async_playwright() as p:
        # 브라우저 실행 (가상 환경)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # 쿠키 주입 (티스토리 세션 유지)
        await context.add_cookies([
            {'name': 'TSSESSION', 'value': os.environ["7c286480388b8be6cabc55802ca8a8ba6099fbf6"], 'domain': '.tistory.com', 'path': '/'}
        ])
        
        page = await context.new_page()
        content = generate_content()
        title = "오늘의 경제 및 과학 리포트"
        
        # 티스토리 글쓰기 페이지 이동 (네 블로그 주소 설정 필요)
        blog_name = os.environ["ideas11199"]
        await page.goto(f"https://{blog_name}.tistory.com/manage/post")
        
        # 제목 및 본문 입력 (티스토리 에디터 구조에 맞춤)
        # ※ 티스토리 에디터 구조에 따라 아래 셀렉터는 업데이트가 필요할 수 있음
        await page.fill('input[name="title"]', title) 
        await page.fill('#editor-root', content) # 기본 에디터 영역
        
        # 발행 버튼 클릭
        await page.click('.btn_primitive.link_complete') # 발행 버튼
        await page.wait_for_timeout(2000)
        
        print(f"[{title}] 포스팅 완료!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_blog())
