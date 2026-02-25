streamlit.errors.StreamlitAPIException: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).

Traceback:
File "/mount/src/doj-dashboard/app.py", line 232, in <module>
    edited_trips = st.data_editor(
        trips_data,
    ...<4 lines>...
        key=f"trips_log_vehicle_{vid}"
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/data_editor.py", line 1071, in data_editor
    _check_type_compatibilities(data_df, column_config_mapping, dataframe_schema)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/data_editor.py", line 606, in _check_type_compatibilities
    raise StreamlitAPIException(
    ...<5 lines>...
    )
