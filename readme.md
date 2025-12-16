# LaTeX Photo Converter
## Team Members

Duncan Truitt (Team Lead), Landon Oelschlaeger (Developer), Jayshon Vernor(Developer/Documentation Lead).

## Project Description

### Introduction
LaTeX is a powerful tool for producing clean and professional documents.
Students often use it to turn in their assignments in a clean, formatted way, as opposed
to turning in handwritten notes and assignments that may not be as legible. However,
as it is often that working out problems by hand on paper is required before converting
that work into LaTeX, we propose a solution to use AI and scanning tools to more
rapidly convert notes and assignments into LaTeX code. We focus particularly on the
conversion of homework assignments into structured LaTeX formats for students, such
that one can simply scan their assignment papers, and have a structured LaTeX
project/document created from it.
### Core Objectives
- Design a phone app that allows the user to scan documents in a manner similar
to an app like camscanner, and then take those documents and convert them to
formatted LaTeX using AI.
- Give users the ability to manage and modify documents and tex files that they
have uploaded/created.
- Implements a file management system to both past photos and their resulting
LaTeX document
- Create and implement an AI workflow for parsing and creating TeX files from
scanned documents.

### Set Up Instructions

To set up the application, make sure that you have docker and [flutter](https://docs.flutter.dev/get-started/quick?_gl=1*ezoz13*_gcl_aw*R0NMLjE3NjU4Mzk0ODkuQ2owS0NRaUFnUF9KQmhELUFSSXNBTnBFTXh3LWlpZWhYRlFlVHdGdXBZb211Z3MyYkxGYkZaVXhueW5aU0FYUmZva09YVzZoUHFEM3Z2b2FBdXFrRUFMd193Y0I.*_gcl_dc*R0NMLjE3NjU4Mzk0ODkuQ2owS0NRaUFnUF9KQmhELUFSSXNBTnBFTXh3LWlpZWhYRlFlVHdGdXBZb211Z3MyYkxGYkZaVXhueW5aU0FYUmZva09YVzZoUHFEM3Z2b2FBdXFrRUFMd193Y0I.*_ga*MTk5MjYyMTk1MC4xNzYyNjIyMjIw*_ga_04YGWK0175*czE3NjU4Mzk0ODkkbzQkZzAkdDE3NjU4Mzk0ODkkajYwJGwwJGgw)
installed. 
After installing flutter run `flutter config --enable-web` once per host to properly
configure flutter for web applications. Once both have been installed and flutter has
been configured ensure docker desktop is running and then execute the following to run
the application (starting from the repo root folder):

```
cd \frontend\web-app\photex
flutter clean
flutter pub get
flutter build web
docker compose down -v
docker compose build
docker compose up
```

Access the application from a browser using (http://127.0.0.1:3001/)
