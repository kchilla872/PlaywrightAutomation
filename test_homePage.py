import sys
import os
import pytest
from locator import *

# Add the current directory to the system path
sys.path.append(os.getcwd())


@pytest.mark.first
def test_TC001_View_Logo(page):
    page.goto(HomePage.Url)
    assert page.locator(HomePage.Logo).is_visible()
    assert "Amazon" in page.title()


@pytest.mark.run(after=test_TC001_View_Logo)
def test_TC002_SearchItem(page):
    page.fill(HomePage.Searchbox, "Wireless Headphones")
    page.click(HomePage.Searchbutton)
    page.wait_for_timeout(5000)


@pytest.mark.run(after=test_TC002_SearchItem)
def test_TC003_AddtoCart(page):
    page.wait_for_selector(HomePage.Firstresult).click()
    page.wait_for_selector(HomePage.Addtocart).click()
    page.wait_for_timeout(4000)


@pytest.mark.run(after=test_TC003_AddtoCart)
def test_TC004_GotoCart(page):
    page.wait_for_selector(HomePage.Firstresult).click()
    page.wait_for_selector(HomePage.Gotocart).click()
    page.wait_for_timeout(3000)


@pytest.mark.run(after=test_TC004_GotoCart)
def test_TC005_ViewCart(page):
    page.wait_for_selector(HomePage.Viewcart).is_visible()


@pytest.mark.run(after=test_TC005_ViewCart)
def test_TC006_Unchecking_Checking_CartItems(page):
    page.wait_for_selector(HomePage.Cartitemradiobutton).click()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.Cartitemradiobutton).click()


@pytest.mark.run(after=test_TC006_Unchecking_Checking_CartItems)
def test_TC007_Save_for_later_CartItems(page):
    page.wait_for_selector(HomePage.Saveforlater).click()



@pytest.mark.run(after=test_TC007_Save_for_later_CartItems)
def test_TC008_Move_for_later(page):
    page.wait_for_selector(HomePage.Moveforlater).click()
    page.wait_for_timeout(1000)


@pytest.mark.run(after=test_TC008_Move_for_later)
def test_TC009_Increment_Decrement_items(page):
    page.wait_for_selector(HomePage.incrementicon).click()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.decrementicon).click()
    page.wait_for_timeout(1000)


@pytest.mark.run(after=test_TC009_Increment_Decrement_items)
def test_TC010_Delete_items(page):
    page.wait_for_selector(HomePage.Delete).is_visible()
    page.wait_for_timeout(1000)
    page.wait_for_selector(HomePage.Delete).click()