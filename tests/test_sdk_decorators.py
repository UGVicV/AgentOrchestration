import pytest
from src.sdk.decorators import task


class TestTaskDecorator:
    def test_valid_retries(self):
        try:
            @task(retries=3, timeout=60)
            async def my_task():
                pass
            assert (
                my_task.__task_config__[
                    "retries"
                ]
                == 3
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_valid_zero_retries(self):
        try:
            @task(retries=0, timeout=60)
            async def my_task():
                pass
            assert (
                my_task.__task_config__[
                    "retries"
                ]
                == 0
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_negative_retries(self):
        try:
            with pytest.raises(
                ValueError,
                match="non-negative",
            ):
                @task(retries=-1)
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_non_int_retries(self):
        try:
            with pytest.raises(
                TypeError,
                match="must be an integer",
            ):
                @task(retries="three")
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_bool_retries(self):
        try:
            with pytest.raises(
                TypeError,
                match="must be an integer",
            ):
                @task(retries=True)
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_negative_timeout(self):
        try:
            with pytest.raises(
                ValueError,
                match="positive",
            ):
                @task(timeout=-10)
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_zero_timeout(self):
        try:
            with pytest.raises(
                ValueError,
                match="positive",
            ):
                @task(timeout=0)
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )

    def test_non_int_timeout(self):
        try:
            with pytest.raises(
                TypeError,
                match="must be an integer",
            ):
                @task(timeout="fast")
                async def my_task():
                    pass
        except Exception as e:
            pytest.fail(
                f"Unexpected exception: {e}"
            )
