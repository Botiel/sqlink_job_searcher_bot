import pprint
from playwright.sync_api import sync_playwright, Page
from datetime import datetime as dt
from config import *


class JobsPage:

    # =========== PAGE ELEMENTS ====================
    job_box_element = '//div[@class="col10"]'
    send_cv_btn = '//a[@id="sendPopupCVinner"]'
    upload_cv_btn = '//input[@class="uploadCVInput"]'
    submit_cv_btn = '//input[@class="uploadButton"]'
    successfully_submitted_element = '//div[@class="thanksPage"]'

    def __init__(self, page: Page, page_number: int):
        self.page = page
        self.curr_page_url = f"{URL}{page_number}"
        self.page_number = page_number
        self.valid_jobs = []
        self.invalid_jobs = []

    @staticmethod
    def clean_text(text: str) -> list[str]:
        return text.lower().replace("-", " ").replace("/", " ").replace('\\', " ").replace(".", " ").split()

    @staticmethod
    def get_job_id(word_list: list[str]) -> str:
        return word_list[word_list.index("משרה:") + 1]

    @staticmethod
    def get_list_of_seen_jobs() -> list:
        try:
            with open(SEEN_JOBS_FILE, "r") as f:
                return [line.replace("\n", "") for line in f.readlines()]
        except FileNotFoundError:
            return []

    def filter_jobs(self, job_box, index: int) -> dict:
        word_list = self.clean_text(job_box.text_content())

        keywords = [key for key in KEY_WORDS if key in word_list]
        languages = [lang for lang in LANGUAGES if lang in word_list]
        avoid = [key for key in AVOID_KEY_WORDS if key in word_list]

        conditions = [
            not avoid,
            not languages or DESIRED_LANGUAGES in languages,
            len(keywords) > 0
        ]

        job = {
            "keywords": keywords,
            "languages": languages,
            "avoid_keywords": avoid,
            "id": self.get_job_id(word_list),
            "index": index
        }

        if all(conditions):
            job["is_valid"] = True
        else:
            job["is_valid"] = False

        return job

    def get_jobs_from_page(self) -> None:

        self.page.goto(self.curr_page_url)
        job_boxes = self.page.query_selector_all(self.job_box_element)
        seen_jobs = self.get_list_of_seen_jobs()

        for i, box in enumerate(job_boxes):
            result = self.filter_jobs(box, index=i)

            if result.get("id") in seen_jobs:
                continue
            else:
                with open(SEEN_JOBS_FILE, "a") as f:
                    f.writelines(f"{result.get('id')}\n")

            if result.get("is_valid"):
                self.valid_jobs.append(result)
            else:
                self.invalid_jobs.append(result)

    def submit_jobs(self) -> None:

        for job in self.valid_jobs:

            job_boxes = self.page.query_selector_all(self.job_box_element)
            box_index = job.get("index")

            job_boxes[box_index].query_selector(self.send_cv_btn).click()
            self.page.set_input_files(selector=self.upload_cv_btn, files=CV_FILE)
            self.page.locator(self.submit_cv_btn).click()

            with open(SUBMIT_LOG_FILE, "a") as f:
                f.writelines(f"Sending cv to job index number: {box_index} | "
                             f"Page Number: {self.page_number} | "
                             f"job id: {job.get('id')} | "
                             f"Date: {dt.now().strftime('%d-%m-%Y')}\n")

            # validating submit
            self.page.wait_for_selector(self.successfully_submitted_element)

            # navigating back to the jobs page
            self.page.goto(self.curr_page_url)

    def debug_print_lists(self) -> None:
        pprint.pprint(self.valid_jobs)
        pprint.pprint(self.invalid_jobs)


class Bot:
    next_page_btn = '//li[@id="rightLeft"]/a'

    @classmethod
    def run_bot(cls, is_headless: bool) -> None:

        print("Bot Initializing...\n")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=is_headless)
            context = browser.new_context()
            page = context.new_page()

            page_number = 1

            while True:
                print(f"Running page number: {page_number}\n")

                bot = JobsPage(page=page, page_number=page_number)
                bot.get_jobs_from_page()
                bot.submit_jobs()

                try:
                    page.wait_for_selector(cls.next_page_btn, timeout=5000)
                except Exception as e:
                    print(f'No more pages...\n{e}')
                    break
                else:
                    page_number += 1


if __name__ == '__main__':
    Bot.run_bot(is_headless=HEADLESS)
