import pytest
from django.conf import settings

from news.forms import CommentForm
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    'create_news_list', ([lazy_fixture('create_news_list')])
)
@pytest.mark.django_db
def test_home_page_news_count(client, create_news_list, home_url, news_data):
    """
    Проверка количества новостей на главной - не более десяти.
    Проверка атрибутов произвольного объекта.
    """
    response = client.get(home_url)
    queryset = response.context['object_list']
    assert queryset.count() <= settings.NEWS_COUNT_ON_HOME_PAGE
    news = queryset[0]
    assert news.title == news_data['title']
    assert news.text == news_data['text']
    assert news.date == news_data['date']
    assert news.author == news_data['author']


@pytest.mark.parametrize(
    'create_news_list', [lazy_fixture('create_news_list')]
)
@pytest.mark.django_db
def test_home_page_news_order(create_news_list):
    """Проверка новостей по убыванию даты."""
    fixture_dates = [news.date for news in create_news_list]
    assert fixture_dates == sorted(fixture_dates, reverse=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'create_comments_list', [lazy_fixture('create_comments_list')]
)
def test_detail_page_comments_order(client, detail_url, create_comments_list):
    """Проверка хронологии комментариев - от старых к новым."""
    response = client.get(detail_url)
    news = response.context['news']
    fixture_comments = create_comments_list.filter(news=news)
    all_timestamps = [comment.created for comment in fixture_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Форма комментария недоступна для гостя."""
    response = client.get(detail_url)
    assert 'form' not in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url):
    """Форма комментария доступна для пользователя."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
