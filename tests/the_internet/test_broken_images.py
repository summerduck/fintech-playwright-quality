"""Tests for Broken Images on The Internet."""

import allure
import pytest

from pages.the_internet.broken_images_page import BrokenImagesPage


@allure.epic("The Internet")
@allure.feature("Broken Images")
class TestBrokenImages:
    """Broken Images test suite for The Internet."""

    @allure.story("Page Load")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Broken Images page loads successfully")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_page_loads_successfully(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify the Broken Images page loads and heading is visible."""
        broken_images_page.navigate()
        broken_images_page.verify_page_loaded()

    @allure.story("Page Content")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Page heading reads 'Broken Images'")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_page_heading_is_broken_images(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify the page heading text reads 'Broken Images'."""
        broken_images_page.navigate()
        broken_images_page.verify_page_loaded()

    @allure.story("Image Count")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Page contains exactly 3 content images")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_total_image_count_is_three(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify the content area contains exactly 3 images."""
        broken_images_page.navigate()
        broken_images_page.verify_total_image_count(3)

    @allure.story("Broken Images")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Page contains exactly 2 broken images")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_broken_image_count_is_two(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify exactly 2 content images have a broken source."""
        broken_images_page.navigate()
        broken_images_page.verify_broken_image_count(2)

    @allure.story("Valid Images")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Page contains exactly 1 valid image")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_valid_image_count_is_one(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify exactly 1 content image has a valid source."""
        broken_images_page.navigate()
        broken_images_page.verify_valid_image_count(1)

    @allure.story("Image Count Consistency")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Broken and valid image counts sum to total")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_broken_plus_valid_equals_total(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify broken + valid image counts equal the total image count."""
        broken_images_page.navigate()
        broken_images_page.verify_broken_plus_valid_equals_total()

    @allure.story("Image Load State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("All images have complete === true when assertions run")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_all_images_complete_at_assertion_time(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify all content images have complete === true after networkidle."""
        broken_images_page.navigate()
        broken_images_page.verify_all_images_complete()

    @allure.story("Image Scope")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GitHub fork banner is not included in content image assertions")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_fork_banner_excluded_from_content_images(
        self,
        broken_images_page: BrokenImagesPage,
    ) -> None:
        """Verify the GitHub fork banner image is outside the content selector."""
        broken_images_page.navigate()
        broken_images_page.verify_fork_banner_not_in_content_images()
