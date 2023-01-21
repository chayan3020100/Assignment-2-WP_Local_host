import requests
import openai
import base64
import os
from dotenv import load_dotenv

load_dotenv()

wp_user = os.getenv("WP_USER")
wp_pass = os.getenv("WP_PASS")
credntial = f'{wp_user}:{wp_pass}'
token = base64.b64encode(credntial.encode())
headers = {'Authorization': f'Basic {token.decode("utf-8")}'}


def open_ai_tool(text):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    data = response.get('choices')[0].get('text').strip().replace('\n', '').replace('\n\n', '')
    return data


def h2(text):
    codes = f'<!-- wp:heading --><h2>{text}</h2><!-- /wp:heading -->'
    return codes


def para(text):
    return f'<!-- wp:paragraph --><p>{text}</p><!-- /wp:paragraph -->'


with open('kw.txt', 'r+') as file:
    reader = file.readlines()
    for kw in reader:
        keyword = kw.strip().replace('\n', '')
        no_best = keyword.strip('best').strip()
        outline_writer = open_ai_tool(
            f'Write a killer blog outline for the following request from a customer.\n\nREQUEST:{no_best}\n\n'
            f'Brainstorm and make a list of sections for this blog post. The outline should meet the customer\'s '
            f'request and each section should be highly descriptive. Do not write any subsection under the main section.\n\n'
            f'SECTIONS:\n\n'
            f'1.')
        single_line = outline_writer.split('.')
        update_outline = []
        for line in single_line:
            if 'Introduction' not in line and 'Conclusion' not in line:
                output = ''.join([i for i in line if not i.isdigit()])
                update_outline.append(output.strip())
        body = ''
        for outline in update_outline:
            headings = h2(outline)
            article = para(open_ai_tool(
                f'"""\nBlog Section Title: {outline}, Main Keyword: {keyword}\n"""\nWrite this blog section into a details professional para, witty and clever explanation:'))
            full_body = headings + article
            body += full_body
        wp_data = {
            'title': keyword.title(),
            'slug': keyword.lower().replace(' ', '-'),
            'status': 'publish',
            'content': body
        }

        post_url = 'https://localhost/wp/wp-json/wp/v2/posts'

        try:
            request = requests.post(post_url, data=wp_data, headers=headers, verify=False)

            if request.status_code == 201:
                print(f'"{keyword}" has posted successfully to your blog!')
            else:
                print('Something went wrong')
        except:
            print('Something went wrong')
