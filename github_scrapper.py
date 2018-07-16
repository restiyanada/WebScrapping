import time, json, requests
from bs4 import BeautifulSoup
import os, random, sys, random
import csv, datetime, re, json
import xlsxwriter, shutil

#commit_url = 'https://github.com/geekcomputers/Python'
#base_url = 'https://github.com/geekcomputers/Python'
#issues_url = 'https://github.com/geekcomputers/Python/issues'
#cntrb_url = 'https://github.com/geekcomputers/Python/commits?author=geekcomputers'

b_url = 'https://github.com'
final_data = []
commit_data = []
#output_file = 'github.xlsx'
basic_data = []
cntrb_data = []
issues_data = []

user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36']

ses = requests.session()
ses.headers['User-Agent'] = random.choice(user_agents)


def parseBasicData():
    global base_url, basic_data, b_url, commit_url, issues_url, cntrb_url
    print ("commit_url", commit_url)
    print ("issues_url", issues_url)
    print ("cntrb_url", cntrb_url)
    try:
        resp = ses.get(base_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        auth_name = parseText(soup.find('span', {'class': 'author'}).text)
        repo_name = parseText(soup.find("h1", {'class': 'public'}).find("strong").text)
        repo_cntt = parseText(
            soup.find("div", {'class': 'repository-meta-content'}).find("span", {'class': 'col-11'}).text)
        a_l = soup.find_all("a", {'class': 'social-count'})
        fork_cnt = issue_cnt = commit_cnt = cntrb_cnt = 0
        for a in a_l:
            txt = a.attrs['aria-label']
            if txt.lower().find('fork') != -1:
                fork_cnt = parseText(a.text)
        cmt_ele = soup.find("li", {'class': 'commits'})
        commit_url = b_url + cmt_ele.find('a').attrs['href']
        commit_cnt = parseText(cmt_ele.find('span', {'class': 'num'}).text)
        a_l = soup.find_all('a', {'class': 'js-selected-navigation-item'})
        for a in a_l:
            txt = a.text.lower()
            if txt.find('issues') != -1:
                issues_url = b_url + a.attrs['href']
                issue_cnt = parseText(a.find('span', {'class': 'Counter'}).text)
        cntrb_ele = soup.find('ul', {'class': 'numbers-summary'})
        li_l = cntrb_ele.find_all('li')
        for li in li_l:
            txt = li.text.lower()
            if txt.find('contributors') != -1:
                cntrb_cnt = parseText(li.find('span', {'class': 'num'}).text)
                cntrb_url = b_url + li.find('a').attrs['href']
        basic_data.append(len(basic_data) + 1)
        basic_data.append(auth_name)
        basic_data.append(repo_name)
        basic_data.append(repo_cntt)
        basic_data.append(fork_cnt)
        basic_data.append(issue_cnt)
        basic_data.append(commit_cnt)
        basic_data.append(cntrb_cnt)  # auth_name, repo_name, repo_cntt, fork_cnt, issue_cnt, commit_cnt, cntrb_cnt
    except:
        pass  # print(basic_data)


def parseCommitData():
    global commit_url, commit_data
    resp = ses.get(commit_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    div_ele = soup.find('div', {'class': 'commits-listing'})
    li_l = div_ele.find_all('li', {'class': 'commits-list-item'})
    for li in li_l:
        try:
            lst = []
            auth = parseText(li.find('a', {'class': 'commit-author'}).text)
            dt = parseText(li.find('relative-time').text)
            cmt_link = b_url + li.find('a', {'class': 'sha'}).attrs['href']
            repo_title = parseText(li.find('p', {'class': 'commit-title'}).text)
            tit_ele = li.find('div', {'class': 'commit-desc'})
            cmt_title = ''
            if tit_ele:
                cmt_title = parseText(tit_ele.text)
            lst.append(len(commit_data) + 1)
            lst.append(auth)
            lst.append(dt)
            lst.append(repo_title)
            lst.append(cmt_link)
            lst.append(cmt_title)
            commit_data.append(lst)  # author, data, repo_name, cmt_link, cmt_tile
        except:
            print("error in commit ")
            pass  # print( commit_data )


def parseContribData():
    global cntrb_url, cntrb_data
    _cntrb_url = cntrb_url + '-data'
    ses.headers['Accept'] = 'application/json'
    ses.headers['origin'] = 'https://github.com'
    ses.headers['Referer'] = cntrb_url
    resp = ses.get(_cntrb_url)
    jsn = json.loads(resp.text)
    for each in jsn:
        try:
            lst = []
            auth = each['author']['login']
            link = b_url + '/' + auth
            weeks = each['weeks']
            cnt = 0
            for week in weeks:
                cnt += week['c']
            lst.append(len(cntrb_data) + 1)
            lst.append(auth)
            lst.append(link)
            lst.append(cnt)
            cntrb_data.append(lst)  # s.no, author name, author link, commit count
        except:
            pass


def parseIssuesData():
    global issues_url, issues_data
    resp = ses.get(issues_url)
    print(issues_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    div_ele = soup.find('ul', {'class': 'js-active-navigation-container'})
    li_l = div_ele.find_all('li', {'class': 'Box-row'})
    for li in li_l:
        try:
            lst = []
            auth = parseText(li.find('a', {'class': 'muted-link'}).text)
            dt = parseText(li.find('relative-time').text)
            iss_link = b_url + li.find('a', {'class': 'link-gray-dark'}).attrs['href']
            repo_title = parseText(li.find('a', {'class': 'link-gray-dark'}).text)
            lst.append(len(issues_data) + 1)
            lst.append(auth)
            lst.append(dt)
            lst.append(repo_title)
            lst.append(iss_link)
            issues_data.append(lst)  # author, date, issues_name, iss_link
        except:
            pass
            print("error in issues ")  # print( issues_data )


def parseText(text):
    while text.find("\t") != -1:
        text = text.replace("\t", "")
    while text.find("\n") != -1:
        text = text.replace("\n", "")
    while text.find("  ") != -1:
        text = text.replace("  ", " ")
    return text


def checkdata(text, fname):
    f = open(fname, "wb")
    f.write(text.encode("utf-8"))
    f.close()


def writeTocsv():
    global output_file
    workbook = xlsxwriter.Workbook(output_file)
    basic_ws = workbook.add_worksheet('Basic')
    cntrb_ws = workbook.add_worksheet('Contributions')
    commt_ws = workbook.add_worksheet('Commits')
    issue_ws = workbook.add_worksheet('Issues')
    b_row = 0
    b_col = 0
    i_row = 0
    i_col = 0
    c_row = 0
    c_col = 0

    b_h = ['S.No', 'Author Name', 'Repository Name', 'Repository Count', 'Fork Count', "Issue Count", "Commit Count",
           "Contribution Count"]
    # auth_name, repo_name, repo_cntt, fork_cnt, issue_cnt, commit_cnt, cntrb_cnt
    for each in b_h:
        basic_ws.write(b_row, b_col, each)
        b_col += 1
    b_row += 1
    b_col = 0
    for lst in basic_data:
        basic_ws.write(b_row, b_col, lst)
        b_col += 1
    c_h = ['S.No', 'Author Name', 'Date', 'Commit Title', 'Commit Link', "Commit Description"]
    # author, data, repo_name, cmt_link, cmt_tile
    for each in c_h:
        commt_ws.write(c_row, c_col, each)
        c_col += 1
    for lst in commit_data:
        c_row += 1
        c_col = 0
        for each in lst:
            commt_ws.write(c_row, c_col, each)
            c_col += 1
    co_h = ['S.no', 'Author name', 'Author link', 'Commit count']
    c_col = 0
    c_row = 0
    for each in co_h:
        cntrb_ws.write(c_row, c_col, each)
        c_col += 1
    for lst in cntrb_data:
        c_row += 1
        c_col = 0
        for each in lst:
            cntrb_ws.write(c_row, c_col, each)
            c_col += 1
    i_h = ['S.No', 'Author Name', 'Date', 'Issue', 'Commit Link', "Issue Link"]
    # author, date, issues_name, iss_link
    for each in i_h:
        issue_ws.write(i_row, i_col, each)
        i_col += 1
    for lst in issues_data:
        i_row += 1
        i_col = 0
        for each in lst:
            issue_ws.write(i_row, i_col, each)
            i_col += 1
    workbook.close()


def init(__commit_url, __cntrb_url, __issues_url, __output_file):
    global output_file, org_url, basic_data, b_url, commit_url, issues_url, cntrb_url, base_url
    global output_file, org_url
    commit_url = __commit_url
    base_url = __commit_url
    cntrb_url = __cntrb_url
    issues_url = __issues_url
    output_file = __output_file

def main():
    print("Lagi proses. . Mohon bersabar . .")
    global output_file, org_url

    parseBasicData()
    parseCommitData()
    parseIssuesData()
    parseContribData()
    writeTocsv()
    print("\nData berhasil diekstrak >> " + output_file)

if __name__ == "__main__":
    main()
