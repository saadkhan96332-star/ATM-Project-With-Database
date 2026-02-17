#Project:4//////////////////////////////////////////////////////////////////////////////////////////////////////
#ATM
import hashlib
import os
from datetime import datetime
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="atm_db",
    auth_plugin="mysql_native_password"
)

cursor = conn.cursor()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////
#Pin Hashing
def hash_pin(pin):

    encoded_pin=str(pin).encode()

    hashed=hashlib.sha256(encoded_pin).hexdigest()

    return hashed

#Save History
def save_history_to_database(acc_no,transaction_type,amount,detail):

    sql="INSERT INTO transactions(acc_no,transaction_type,amount,detail)VALUES (%s,%s,%s,%s)"

    data=(acc_no,transaction_type,amount,detail)

    cursor.execute(sql,data)

    conn.commit()

    
#Create New Account
def create_new_account():

    print("1.For saving account")
    print("2.For current account")

    acc_type=int(input("enter account type: "))

    x=int(input("enter how much account you want to create: "))

    for i in range(1,x+1):
        print(f"Account no {i} info")
        acc_no=int(input("enter account no: "))
        acc_holder_name=input("enter name: ")
        pin=input("enter pin: ")

        hashed_pin=hash_pin(pin)

        balance=int(input("enter balance: "))

        if(acc_type==1):
            acc_type="saving account"    
        else:
            acc_type="current account"
           

        sql="""INSERT INTO accounts(acc_no,acc_holder_name,pin,balance,acc_type)
        VALUES(%s,%s,%s,%s,%s)
        """
        data=(acc_no,acc_holder_name,hashed_pin,balance,acc_type)

        cursor.execute(sql,data)

        conn.commit()

        print(f"Account of {acc_holder_name} created successfully\n")

 
#Login Logic
def login():
    
    acc_no=int(input("enter account No: "))
    
    attempt=3

    while attempt >0:
        pin=int(input("enter pin: "))

        hashed_pin=hash_pin(pin)

        sql="""SELECT acc_no,acc_holder_name,pin,balance,acc_type
            FROM accounts
            WHERE acc_no=%s AND pin=%s
            """
        cursor.execute(sql,(acc_no,hashed_pin))

        user=cursor.fetchone()

        if user:
            acc_no=user[0]

            print(f"\n....Welcome {user[1]}....")
            user_menu(acc_no)
            return
        else:
            attempt-=1
            print(f"Wrong Pin:Try Left:{attempt} ")

    print("Account Looked due to wrong pin\n") 
    
#Check Balance
def check_balance(acc_no):

    sql="SELECT balance FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    result=cursor.fetchone()

    if result:
        print(f"Your current balance is:{result[0]}\n")
    else:
        print("Account not found\n")


#Withdrawl
def withdraw(acc_no):

    amount=int(input("enter amount to withdrawl: "))

    sql="SELECT balance,acc_type FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    result=cursor.fetchone()

    if not result:
        print("Account is not found\n")
        return
    
    balance,acc_type=result

    if acc_type=="saving account" and balance-amount<1000:
        print("Insufficient balance: Minimum 1000 required for saving account\n")
        return
    elif acc_type=="current account" and balance-amount<-5000:
            print("Insufficient balance: Overdraft limit exceeded for current account\n")
            return
    elif amount<=0:
        print("invalid amount\n")
        return
    
    new_balance=balance-amount

    sql="UPDATE accounts SET balance=%s WHERE acc_no=%s"

    cursor.execute(sql,(new_balance,acc_no))

    conn.commit()

    save_history_to_database(acc_no,"withdraw",amount,"cash with draw")

    print(f"Withdrawal successful! Your new balance is: {new_balance}\n")


#Deposit
def deposit(acc_no):

    amount=int(input("enter amount to deposit: "))
            
    if amount<=0:
        print("invalid amount\n")
        return
    
    sql="SELECT balance FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    result=cursor.fetchone()

    if not result:
        print("Account not found\n")
        return
    
    balance=result[0]

    new_balance=balance+amount

    sql="UPDATE accounts SET balance=%s WHERE acc_no=%s"

    cursor.execute(sql,(new_balance,acc_no))

    conn.commit()
    
    save_history_to_database(acc_no,"deposit",amount,"cash deposit")

    print(f"Deposit successful! Your new balance is: {new_balance}\n")


#Change Pin
def change_pin(acc_no):

    attempt=3

    while attempt>=1:

        old_pin=int(input("enter old pin: "))

        hashed_old_pin=hash_pin(old_pin)

        sql="SELECT pin FROM accounts WHERE acc_no=%s"

        cursor.execute(sql,(acc_no,))

        result=cursor.fetchone()

        current_pin=result[0]

        if current_pin==hashed_old_pin:

            new_pin=int(input("enter new pin: "))
            confirm_pin=int(input("Confirm new pin: "))

            if new_pin!=confirm_pin:
                print("Wrong Confirm Password!Try again")
                continue

            hashed_new_pin=hash_pin(new_pin)

            sql="UPDATE accounts SET pin=%s WHERE acc_no=%s"

            cursor.execute(sql,(hashed_new_pin,acc_no))

            conn.commit()

            save_history_to_database(acc_no,"Pin Change",0,"Pin change")
            
            print("Password Change Successfully\n")
            return
        else:
            attempt-=1

            print(f"You have left :{attempt} try")

    print("Pin is not change!To many Try")


#Check Account Info
def check_account_info(acc_no):

    sql="SELECT acc_no,acc_holder_name,balance FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    result=cursor.fetchone()
    
    if result:
        print("--------------------------")

        print(f"Account no: {result[0]}")
        print(f"Account Name:{result[1]}")
        print(f"Balance:{result[2]}")

        print("--------------------------\n")
    else:
        print("Account not found\n")
        return


#View History
def view_history_of_account(acc_no,limit=5):

    sql="SELECT transaction_type,amount,transaction_date FROM transactions Where acc_no=%s ORDER BY transaction_date DESC LIMIT %s"

    cursor.execute(sql,(acc_no, limit))

    rows=cursor.fetchall()
    
    print(f"Last {limit} transaction for account:{acc_no}")

    print("-----------------------------------------")
    for row in rows:
        print(f"{row[2]} - {row[0]} - {row[1]}")
    
    print("-----------------------------------------\n")


#Transfer Money
def transfer_money_to_another_account(acc_no):

    to_acc=int(input("enter account no to transfer: "))

    amount=int(input("enter amount to tranfer: "))
    
    if amount<=0:
        print("enter invalid amount\n")
        return
    
    if acc_no==to_acc:
        print("money cannot tranfer to same account\n")
        return


    sql="SELECT balance,acc_type FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    sender=cursor.fetchone()

    if not sender:
        print("Your account not found!")
        return
    
    sender_balance,acc_type=sender

    if acc_type=="saving account" and sender_balance - amount<1000:
        print("Minimum amount required:1000")
        return
    
    if acc_type=="current account" and sender_balance - amount < -5000:
        print("Overdraft limit exceeded for current account\n")
        return
    
    sql="SELECT balance FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(to_acc,))

    receipt=cursor.fetchone()

    if not receipt:
        print("Account not found\n")
        return
    
    receipt_balance=receipt[0]

    try:

        #SENDER LOGIC
        new_sender_money=sender_balance-amount

        new_receipt_money=receipt_balance+amount

        sql="UPDATE accounts SET balance=%s WHERE acc_no=%s"

        cursor.execute(sql,(new_sender_money,acc_no,))
        
        #RECEIVER LOGIC
        sql="UPDATE accounts SET balance=%s WHERE acc_no=%s"

        cursor.execute(sql,(new_receipt_money,to_acc,))
        
        #SENDER HISTORY
        save_history_to_database(acc_no,"Transfer sent",amount,f"sent to:{to_acc}")

        #RECEIVER HISTORY
        save_history_to_database(to_acc,"Transfer received",amount,f"From account:{acc_no}")

        conn.commit()
        print(f"Amount {amount} transferred successfully\n")

    except Exception as e:
        conn.rollback()
        print("Transfer failed:", e)


#Usermenu
def user_menu(acc_no):
    while True:
                    
        print("1.Check Balance")
        print("2.For Withdraw")
        print("3.For Deposit")
        print("4.For Change Pin")
        print("5.For check your account detailed")
        print("6.To check history")
        print("7.For transfer money")
        print("8.For Logout\n")

        ch=int(input("enter your choice: "))

        match ch:

            case 1:
                check_balance(acc_no)
            case 2:
                withdraw(acc_no)
            case 3:
                deposit(acc_no)
            case 4:
                change_pin(acc_no)
            case 5:
                check_account_info(acc_no)
            case 6:
                view_history_of_account(acc_no)
            case 7:
                transfer_money_to_another_account(acc_no)
            case 8:
                print("Logged out\n")
                break
            case _:
                print("Invalid choice\n")


#Admin TO View Account
def view_account():
    
    sql="SELECT acc_no,acc_holder_name,balance,acc_type FROM accounts"

    cursor.execute(sql)

    accounts=cursor.fetchall()
    print("----All Accounts----")
    print("-------------------------------------------------------------------------------------")
    for acc in accounts:
        print(f"Acc No:{acc[0]},Acccount Name:{acc[1]},Balance:{acc[2]},Account Type:{acc[3]}")
    
    print("-------------------------------------------------------------------------------------\n")


#History TO Admin
def view_history_of_account_by_admin():

    acc_no=int(input("enter account no: "))

    sql="SELECT acc_no,transaction_type,amount,transaction_date FROM transactions WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    record=cursor.fetchall()

    if not record:
        print("No record found\n")
        return
    
    print("-----Transaction History-----")

    for h in record:
        print(f"Acc No:{h[0]},Type:{h[1]},Amount:{h[2]},Date:{h[3]}")


#Delete Account
def delete_acoount():
    
    acc_no=int(input("enter account no: "))

    sql="SELECT acc_no From accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    account=cursor.fetchone()

    if not account:
        print("account not found\n")
        return
    

    sql="DELETE FROM transactions WHERE acc_no=%s"
   

    cursor.execute(sql,(acc_no,))

    sql="DELETE FROM accounts WHERE acc_no=%s"

    cursor.execute(sql,(acc_no,))

    print(f"Account No:{acc_no} and its History deleted successfully\n")

    conn.commit()


#Admin Change Password
def change_admin_pin():

    old_pin=int(input("enter old password: "))

    hash_old_pin=hash_pin(old_pin)

    sql="SELECT pin FROM admin_pin"

    cursor.execute(sql)

    current_pin=cursor.fetchone()[0]

    if current_pin==hash_old_pin:

        attempt=3

        while attempt>=1:

            new_pin=int(input("enter new pin: "))
            hash_new_pin=hash_pin(new_pin)

            confirm_pin=int(input("Confirm pin: "))
            hash_confirm_pin=hash_pin(confirm_pin)

            if(hash_new_pin==hash_confirm_pin):
                

                sql="UPDATE admin_pin SET pin=%s"

                cursor.execute(sql,(hash_new_pin,))

                print("Pin Change Successfully\n")

                conn.commit()
                break
            else:
                print(f"Wrong confirm Pin!Try Left:{attempt}")
    else:
            
        print(f"Wrong Old Pin\n")


#Admin Mainmenu
def admin_panel_menu():
   
    
    print("....Welcome To Admin Panel.....\n")
    while True:
        
        print("1.For View All account")
        print("2.Create New Account")
        print("3.To View History")
        print("4.For Change Admin Password")
        print("5.Delete Account")
        print("6.To Logout\n")

        ch=int(input("enter your choice: "))

        match ch:

            case 1:
                view_account()
            case 2:
                create_new_account()
            case 3:
                view_history_of_account_by_admin()
            case 4:
                change_admin_pin()
            case 5:
                delete_acoount()
            case 6:
                print("Thank you\n")
                return
            case _:
                print("invalid choice\n")


#Admin Login
def admin_login():
   
    attempt=3

    while attempt>=1:

        pin=int(input("enter admin password: "))

        hash_admin_pin=hash_pin(pin)
       
        sql="SELECT pin FROM admin_pin LIMIT 1"

        cursor.execute(sql)

        password=cursor.fetchone()[0]

        if password==hash_admin_pin:
            print("Login Successfully")
            admin_panel_menu()
            return  
        else:
            attempt-=1
            print(f"Wrong Password!Try Left:{attempt}")

    print("Fail To Login\n")


#Program Start
while True:
        
    print("1.For User")
    print("2.For Admin Panel")
    print("3.For Exit\n")

    ch=int(input("enter your choice: "))
 
    if(ch==1):
        login()     
    elif(ch==2):
        admin_login()
    elif(ch==3):
        print("Thank you\n")
        break
    else:
        print("Invalid choice\n")         