# Webapp for automatic grading

A lot of techers, expecially the university teaches, have problem with grading after the test. They bunch of papers and after they grade them, their work doesn't finish. Then then need to assign grades and points to students in to the school system. Sometimes they even have to send the evaluated tests directly to students. 

However most of the school information systems provide and API for exporting or importing the grades in .csv files. Every student also have his/her own personal id number, which belons to him during the whole stay at university. These two were the main reasons why we decided to develop a solution for automizing the step in between the teach and the school system. 



## Getting Started

After cloning the repository ake sure you have installed Python 3.x. To fulfull all requirements proceed these comands.
```
pip freeze > requirements.txt
pip install -r requirements.txt
```
Then execute the following command and your application will run on localhost.

```
python3 app.py
```

## Contributing

There is wide range for improvement in our app. We would be grad for anybody, who wants to contribute.

## TODO

#### PDF related
 * [x] Merge two pdfs into one - creating overlay with our structure
 * [x] Split pdfs by our structure
 * [ ] Try to use different structure of code because problems with poppler
 * [x] Export splitted pdfs of students and csv file with results
 
#### Data extractions
 * [x] Extract information from our structure - ID of student, grade, points
 * [ ] Add posisions to written ID or name (username) and try to extract it with CNN model learnt on emnist - Hany have 98 % model
 * [ ] Solve czech characters, either
   * find different dataset with czech diacritics
   * enrich emnist dataset by letters with diacritics 
   * Add second clasifier, that would recognize diacritics  / accute(') / carron(ˇ) / none  / 
   * Create our own, small dataset (maybe adding the diacritics to current dataset)
    and use methods here: https://arxiv.org/pdf/1904.08095.pdf
    
#### Web related
 * [x] Write functional web communication.
 * [ ] Get rid of the assets file structure!!! IMPORTANT - not good
 * [ ] Fix Flask
 * [ ] Asynchronous file upload (maybe skip to next)
 * [ ] Rewrite the application into django

## Authors

* **Samuel Fabo** - *web app developemet* - developed the Flask application
* **Jiri Hanus** - *backend developement* - developed .pdf hierarchy functions
* **Richard Stetka** - *graphic designer* - design of header, created web page in Pingendo
* **Petra Rudolfova** - *graphic designer* - design of logo, created video about app
* **Milan Zongor** - *image processing developer* - developed mark recognition

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
