import os
import asyncio
from google import genai
from playwright.async_api import async_playwright

async def post_to_blog():
    # 1. 환경 변수 로드 및 체크
    api_key = os.environ.get("AIzaSyDt0DhZuAn_i1jPTkhsjU2ZEz1brbf-qVs")
    ts_session = os.environ.get("7c286480388b8be6cabc55802ca8a8ba6099fbf6")
    blog_name = os.environ.get("ideas11199")

    if not all([api_key, ts_session, blog_name]):
        print("에러: GitHub Secrets(GEMINI_API_KEY, TISTORY_SESSION, TISTORY_BLOG_NAME)를 확인해라.")
        return

    # 2. Gemini AI용 전문 프롬프트 (C-Rank, DIA, 금칙어 반영)
    client = genai.Client(api_key=api_key)
    
    # 관심사에 맞춘 고수준 프롬프트 설계
    prompt = """
    당신은 물리 및 IT 기술 전문 블로거입니다. 다음 지침에 따라 티스토리 포스팅을 HTML 형식으로 작성하세요.

    1. 주제: 최신 IT 기술 동향 또는 고등 수준의 물리 개념(역학, 전자기학 등) 중 하나를 선정.
    2. C-Rank 대응: 단순히 긁어온 정보가 아니라, 해당 분야의 전문 지식을 바탕으로 논리적인 분석을 포함할 것.
    3. DIA 대응: 독자가 실제로 궁금해할 법한 질문에 답을 제시하고, 구체적인 사례나 비유를 들어 가독성을 높일 것.
    4. 금칙어 및 SEO: 
       - 상업적 홍보 문구(대출, 도박, 다단계 등) 절대 금지.
       - '이 글은 소정의 원고료를...', '추천합니다' 등 뻔한 광고성 멘트 제외.
       - 자연스러운 문체를 사용하고 키워드를 억지로 반복하지 말 것.
    5. 구조: 
       - <h2>, <h3> 태그를 사용하여 목차를 구성할 것.
       - 본문은 1500자 이상의 풍부한 내용을 담을 것.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        content_html = response.text
        title = "최신 기술 및 물리 개념 심층 분석" # 제목은 동적으로 생성하게 바꿀 수도 있음
    except Exception as e:
        print(f"Gemini 생성 에러: {e}")
        return

    # 3. Playwright 자동화 포스팅
    async with async_playwright() as p:
        try:
            # 브라우저 실행
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # 티스토리 세션 주입 (로그인 우회)
            await context.add_cookies([
                {'name': 'TSSESSION', 'value': ts_session, 'domain': '.tistory.com', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # 티스토리 글쓰기 페이지 접속
            write_url = f"https://{blog_name}.tistory.com/manage/post"
            await page.goto(write_url)
            await page.wait_for_load_state("networkidle")

            # 제목 입력 (티스토리 에디터 선택자 확인 필요)
            # 일반적인 티스토리 에디터 제목 ID는 #mceu_... 혹은 별도 input임
            try:
                await page.fill('input[name="title"]', title) 
            except:
                await page.type('#mceu_18-inp', title) # 구버전 에디터 대비용

            # 본문 입력 (iframe 내부 혹은 콘텐츠 영역 접근)
            # 티스토리는 보통 iframe 내부의 #tinymce 영역을 사용함
            await page.evaluate(f'if(document.querySelector("#tinymce")) {{ document.querySelector("#tinymce").innerHTML = `{content_html}`; }}')
            
            # 발행 버튼 클릭 (선택자는 티스토리 테마/버전에 따라 다를 수 있음)
            # 가장 확실한 건 '발행' 텍스트가 있는 버튼을 찾는 것
            await page.click('button:has-text("발행")')
            await asyncio.sleep(2)
            await page.click('#publish-button') # 최종 확인 버튼

            print(f"[{blog_name}] 포스팅 완료 성공!")
            
        except Exception as e:
            print(f"Playwright 실행 에러: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(post_to_blog())
