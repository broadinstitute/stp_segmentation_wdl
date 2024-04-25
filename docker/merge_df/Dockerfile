FROM python:3.8.16
RUN pip3 install pandas
COPY merge_dfs.py /opt/merge_dfs.py
RUN chmod +x /opt/merge_dfs.py
#CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]
