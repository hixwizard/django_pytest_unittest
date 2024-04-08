import pytest

from news.forms import CommentForm
from django.conf import settings

from news.models import News

pytestmark = pytest.mark.django_db


def test_news_count(client, url_home, list_news):
    """
    Проверка количества новостей на главной - не более десяти.
    Проверка атрибутов произвольного объекта.
    """
    response = client.get(url_home)
    queryset = response.context['object_list']
    assert queryset.count() <= settings.NEWS_COUNT_ON_HOME_PAGE
    first_news = queryset.first()
    news_fields = [field.name for field in News._meta.fields]
    for field_name in news_fields:
        assert hasattr(first_news, field_name)


def test_home_page_news_order(client, url_home, list_news):
    """Проверка новостей по убыванию даты."""
    response = client.get(url_home)
    object_list = response.context['object_list']
    dates = [list_news.date for list_news in object_list]
    assert sorted(dates, reverse=True) == dates


def test_detail_page_comments_order(client, list_news, url_detail):
    """Проверка хронологии комментариев - от старых к новым."""
    response = client.get(url_detail)
    news = response.context['news']
    all_comments = news.comment_set.all()
    dates = [comment.created for comment in all_comments]
    assert dates == sorted(dates)


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    ),
)
def test_form_for_anonymous_and_authorized_clients(
        parametrized_client,
        form_in_context,
        url_detail,
):
    """
    Форма комментария недоступна для гостя.
    Форма комментария доступна для пользователя.
    """
    response = parametrized_client.get(url_detail)
    have_form = 'form' in response.context
    assert have_form is form_in_context
    if have_form:
        assert isinstance(response.context['form'], CommentForm)
