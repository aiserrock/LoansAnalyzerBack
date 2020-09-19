# LoansAnalyzerAPI by aiserrock
## Open source progect for free use, more details here: 
<details>
<summary>Expand</summary>
<p>  
  Loans Analyzer is a completely free open source tool
source code for accounting, viewing, analysis, tracking loans with
using any device that supports the browser.  
  
  
***  


  Loans Analyzer allows you to work with loans from anywhere in the world, where
there is internet. The application(backend) is developed (at the moment only by the author, but
further enthusiasts) for ordinary people who are ready to issue
loans and are not ready to waste their time trying to understand
tools of the program and make calculations using different formulas.   

***  


  The author set himself the task of developing a web application for working with
loans, which:  
1. determines overdue loans,  
2. automatically calculates the income of the lender (from investments under  
percent) for all time, as well as in real time  
3. Automatically calculates the lender's loss (from an investment under  
interest), i.e. unreturned money  
4. Gives the borrower access to a page with a detailed  
information on debt and payment history,  
5. sends to the borrower a payment schedule - a table with detailed,  
information in which month how much money to pay,  
6. conducts analytics of the history of loans of a specific person with the aim of  
approval / disapproval of a loan.  


***
The main idea of the application functioning:  
There are 2 types of users:  
  1. authorized user (keep track of issued loans and income from
them; has full access to the functionality of the application, independently
enters into the system the amount repaid by the borrower)  
  2. unauthorized user (the borrower who received
loan and has access only to the balance tracking page
debt, payment history and payment schedule)  
</p>
</details>  

<details>
<summary>Expand (Russian)</summary>
<p>  
  Loans Analyzer – это полностью бесплатный инструмент с открытым
исходным кодом, для учета, просмотра, анализа, отслеживания займов с
использованием любых устройств, которые поддерживают браузер.  
***   

Loans Analyzer позволяет работать с займами из любой точки мира, где
есть интернет. Приложение разработано (на данный момент только автором, но
в дальнейшем энтузиастами) для обычных людей, которые готовы выдавать
займы и не готовы тратить свое время на то чтобы долго разбираться в
инструментах программы и производить расчеты по разным формулам.  
***   


Автор поставил себе задачу – разработать веб-приложение для работы с
займами, которое:  
1. определяет просроченные займы,
2. автоматически высчитывает доход заимодателя (от вложения под
проценты) за все время, а также в реальном времени
3. автоматически высчитывает убыток заимодателя (от вложения под
проценты), т.е невозвращенные деньги
4. предоставляет займополучателю доступ к странице с подробной
информацией о задолженности и историей выплат,
5. высылает займополучателю график платежей – таблица с подробной
информацией в какой месяц сколько денег нужно заплатить,
6. ведет аналитику истории займов конкретного человека с целью
одобрения/неодобрения выдачи займа.  

Основная идея функционирования приложения:  
Имеются 2 вида пользователей:  
1. авторизованный пользователь (отслеживать выданные займы и доход с
них; имеет полный доступ к функционалу приложения, самостоятельно
вносит в систему сумму, которую погасил заемщик)
2. неавторизованный пользователь (займополучатель, который получил
займ и имеет доступ только к странице отслеживания остатка по
задолженности, истории выплат и графика платежей)
</p>
</details>   

- Use framework FastApi: https://fastapi.tiangolo.com/tutorial/first-steps/  
- Docs: https://loans-analyzer.herokuapp.com/docs#/  
- Deployed app: https://loans-analyzer-front.herokuapp.com/    
- Client-side source code: https://github.com/aiserrock/LoansAnalyzerFront    

## Authorization   
login: `test`  
password: `qwerty` 

                                                                        
 ***
 For start it on yoyr machine do this:  
      1. install all dependencies from requirements.txt           
      2. in console write this: `uvicorn main:app --reload`

