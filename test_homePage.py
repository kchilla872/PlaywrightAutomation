import sys
import os
import pytest
from locators import *

# Add the current directory to the system path
sys.path.append(os.getcwd())


@pytest.mark.order(1)
def test_TC001_View_Logo(page):
    page.goto(HomePage.Url)
    assert page.locator(HomePage.Logo).is_visible()
    assert "Amazon" in page.title()


@pytest.mark.order(2)
def test_TC002_SearchItem(page):
    page.fill(HomePage.Searchbox, "Wireless Headphones")
    page.click(HomePage.Searchbutton)
    page.wait_for_timeout(5000)


@pytest.mark.order(3)
def test_TC003_AddtoCart(page):
    page.fill(HomePage.Searchbox, "Wireless Headphones")
    page.click(HomePage.Searchbutton)
    page.wait_for_selector(HomePage.Firstresult).click()
    page.wait_for_selector(HomePage.Addtocart).click()
    page.wait_for_timeout(4000)
    try:
        page.wait_for_selector(HomePage.PopupCloseButton, state="visible", timeout=5000)
        page.click(HomePage.PopupCloseButton)
    except:
        pass
    page.wait_for_timeout(4000)


@pytest.mark.order(4)
def test_TC004_GotoCart(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_timeout(3000)


@pytest.mark.order(5)
def test_TC005_ViewCart(page):
    page.wait_for_selector(HomePage.Viewcart).is_visible()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.Viewcart).click()


@pytest.mark.order(6)
def test_TC006_Unchecking_Checking_CartItems(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_selector(HomePage.Cartitemradiobutton).click()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.Cartitemradiobutton).click()


@pytest.mark.order(7)
def test_TC007_Save_for_later_CartItems(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_selector(HomePage.Saveforlater, state="visible", timeout=10000)
    page.click(HomePage.Saveforlater)


@pytest.mark.order(8)
def test_TC008_Move_to_cart(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_selector(HomePage.Movetocart).click()
    page.wait_for_timeout(1000)


@pytest.mark.order(9)
def test_TC009_Increment_Decrement_items(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_selector(HomePage.incrementicon).click()
    page.wait_for_timeout(1000)


@pytest.mark.order(10)
def test_TC010_Delete_items(page):
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_selector(HomePage.Delete).is_visible()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.Delete).click()