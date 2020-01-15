FROM python3-onbuild

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    python-pip --upgrade python-pip

RUN pip install --upgrade pip

RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install python 3
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    pkg-config \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# install additional python packages
RUN pip3 install pyproj
RUN pip3 install pyshp
RUN pip3 install ipython
RUN pip install jupyter
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install scikit-learn
RUN pip3 install missingno
RUN pip3 install scipy
RUN pip3 install seaborn
#RUN pip install nltk
RUN pip3 install boto3
RUN pip3 install requests
RUN pip3 install plotly
RUN pip3 install beautifulsoup4
RUN pip3 install matplotlib
RUN pip3 install tqdm
RUN pip3 install lxml


RUN pip3 install luigi

RUN pip3 install jupyter
RUN pip install --upgrade awscli


# dump package lists
RUN dpkg-query -l > /dpkg-query-l.txt \
 && pip2 freeze > /pip2-freeze.txt \
 && pip3 freeze > /pip3-freeze.txt


#RUN pip3 install https://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz

# for jupyter
EXPOSE 8888

WORKDIR /src/outputs

ADD ./classification_csv_gen /src/outputs/
ADD ./EDA /src/outputs/
ADD ./Part1 /src/outputs/
ADD ./Part2 /src/outputs/
ADD ./part2_Classification /src/outputs/
ADD ./Part2_FeatureSelections /src/outputs/
ADD ./Part2_prediction /src/outputs/


#testing




CMD ["python", "./part1.py"]
CMD ["python", "./part2.py"]
CMD ["python", "./classification_csv_gen.py"]