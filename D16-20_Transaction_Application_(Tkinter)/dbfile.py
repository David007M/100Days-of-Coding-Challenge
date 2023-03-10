import sqlite3
from datetime import datetime
import smtplib
from random import randint


class OneUser:
    def __init__(self):
        self.conn = sqlite3.connect('myproject.db')
        self.curs = self.conn.cursor()

    def get_details(self, name):
        self.curs.execute('SELECT * FROM users where name = ?', [name])
        user_details = self.curs.fetchone()
        self.id = user_details[0]
        self.name = user_details[1]
        self.email = user_details[2]
        self.address = user_details[3]
        self.dob = user_details[4]
        self.phone = user_details[5]
        self.password = user_details[6]
        self.upi = user_details[7]
        self.recent = user_details[8]
        self.photo = user_details[9]
        self.curs.execute('SELECT * FROM banks where id = ?', [self.id])
        bank_details = self.curs.fetchone()
        self.bank = bank_details[1]
        self.account = bank_details[2]
        self.balance = bank_details[3]
        return user_details + bank_details

    def insert_record(self, *create_details):
        acc_no = create_details[-1]
        bankid = create_details[-2]
        try:
            self.curs.execute(f'SELECT id FROM banks WHERE account = {acc_no}')
            id = self.curs.fetchone()[0]
            self.curs.execute(
                f'INSERT INTO users (id,name,email,dob,phone,address, password, upi) VALUES({id},?,?,?,?,?,?,?)', create_details[:-2])
            self.conn.commit()
            # self.get_details()
            return 1
        except Exception as e:
            print(e)
            return -1
        return -1

    def check_balance(self, uid, upikey):
        try:
            if self.upi != upikey:
                return -1
            self.curs.execute(
                f"SELECT balance FROM banks WHERE id = {self.id} ")
            bal = self.curs.fetchone()[0]
            return bal
        except Exception as e:
            print(e)
            return -1
        return -1

    def pay(self, accno, accmoney):
        accmoney = int(accmoney)
        self.curs.execute(f"SELECT balance FROM banks WHERE id = ?", [self.id])
        tbal = self.curs.fetchone()[0]
        self.curs.execute(f"SELECT balance FROM banks WHERE account = {accno}")
        rbal = int(self.curs.fetchone()[0])
        sender = self.name
        self.curs.execute(f"SELECT id from banks WHERE account = ?", [accno])
        receiverid = self.curs.fetchone()[0]
        self.curs.execute(f"SELECT name from users WHERE id = ?", [receiverid])
        receiver = self.curs.fetchone()[0]
        self.curs.execute(f"SELECT recent from users WHERE id = ?", [self.id])
        senderrec = self.curs.fetchone()[0]
        self.curs.execute(f"SELECT balance from banks WHERE id = ?", [self.id])
        sendermon = self.curs.fetchone()[0]
        if not senderrec:
            senderrec = [sendermon]
        else:
            senderrec = eval(senderrec)
        self.curs.execute(
            f"SELECT recent from users WHERE id = ?", [receiverid])
        receiverrec = self.curs.fetchone()[0]
        self.curs.execute(
            f"SELECT balance from banks WHERE id = ?", [receiverid])
        receivermon = self.curs.fetchone()[0]
        if not receiverrec:
            receiverrec = [receivermon]
        else:
            receiverrec = eval(receiverrec)
        try:
            self.curs.execute(
                f"UPDATE banks SET balance = {rbal + accmoney} WHERE account = '{accno}'")
            self.curs.execute(
                f"UPDATE banks SET balance = {tbal - accmoney} WHERE account = '{self.account}'")
            if tbal-accmoney < 0:
                return 'lowbal'

            self.curs.execute(f"INSERT INTO transact VALUES (?,?,?,?,?,?)", [
                self.account, accno, accmoney, datetime.now(), sender, receiver])
            senderrec.append(tbal-accmoney)
            receiverrec.append(rbal+accmoney)
            self.curs.execute(f"UPDATE users SET recent = ? WHERE id = ?",
                              [str(senderrec), self.id])
            self.curs.execute(f"UPDATE users SET recent = ? WHERE id = ?",
                              [str(receiverrec), receiverid])
            self.conn.commit()
            return 1
        except Exception as e:
            print(e)
            return -1

    def update_record(self, uid, email, phone, address):
        self.curs.execute(f"UPDATE users SET email = ?, phone = ?, address = ?  WHERE id = ?", [
            email, phone, address, uid])
        self.conn.commit()
        return 1

    def change_password(self, name, passwd):
        print(name, passwd)
        self.curs.execute(f"UPDATE users SET password = ? WHERE name = ?",
                          [passwd, name])
        self.conn.commit()
        return 1

    def otp_change_password(self, email, passwd):
        self.curs.execute(f"UPDATE users SET password = ? WHERE email = ?",
                          [passwd, email])
        self.conn.commit()
        return 1

    def transaction_history(self, uid):
        self.curs.execute(
            f"SELECT * FROM transact WHERE fromacc = ? OR toacc = ?", [uid, uid])
        return self.curs.fetchall()

    def pay_friend(self, uid, sname, fname, fmoney):
        self.curs.execute(f"SELECT id FROM users WHERE name = ?", [fname])
        friendid = self.curs.fetchone()[0]
        self.curs.execute(
            f"SELECT balance,account from banks WHERE id = ?", [friendid])
        friendmon, friendacc = self.curs.fetchone()
        self.curs.execute(
            f"SELECT balance,account from banks WHERE id = ?", [uid])
        sendermon, senderacc = self.curs.fetchone()
        self.curs.execute(f"SELECT recent from users WHERE id = ?", [uid])
        senderrec = self.curs.fetchone()[0]
        if not senderrec:
            senderrec = [sendermon]
        else:
            senderrec = eval(senderrec)
        if len(senderrec) > 30:
            senderrec.pop(0)
        self.curs.execute(f"SELECT recent from users WHERE id = ?", [friendid])
        receiverrec = self.curs.fetchone()[0]

        if not receiverrec:
            receiverrec = [friendmon]
        else:
            receiverrec = eval(receiverrec)
        if len(receiverrec) > 30:
            receiverrec.pop(0)
        if sendermon-fmoney < 0:
            return 'lowbal'
        self.curs.execute(
            f"UPDATE banks SET balance = {friendmon + fmoney} WHERE id = '{friendid}'")
        self.curs.execute(
            f"UPDATE banks SET balance = {sendermon - fmoney} WHERE id = '{uid}'")

        self.curs.execute(f"INSERT INTO transact VALUES (?,?,?,?,?,?)", [
            senderacc, friendacc, fmoney, datetime.now(), sname, fname])
        senderrec.append(sendermon-fmoney)
        receiverrec.append(friendmon+fmoney)
        self.curs.execute(f"UPDATE users SET recent = ? WHERE id = ?",
                          [str(senderrec), uid])
        self.curs.execute(f"UPDATE users SET recent = ? WHERE id = ?",
                          [str(receiverrec), friendid])
        self.conn.commit()
        return 1

    def search_friend(self, value):
        print(value, type(value))
        if value.isalpha():
            self.curs.execute(
                f"SELECT name FROM users WHERE name = ?", [value])
            result = self.curs.fetchone()[0]
            return result
        elif value.isnumeric():
            self.curs.execute(
                f"SELECT name FROM users WHERE phone = ?", [int(value)])
            result = self.curs.fetchone()[0]
            return result

    def friend_info(self, value):
        self.curs.execute(
            f"SELECT id,image FROM users WHERE name = ?", [value])
        id, image = self.curs.fetchall()[0]
        self.curs.execute(f"SELECT account FROM banks WHERE id = ?", [id])
        return self.curs.fetchone()[0], image

    def retrieve_recent(self, uid):
        self.curs.execute("SELECT recent FROM users WHERE id = ?", [uid])
        return self.curs.fetchone()[0]

    def clear_recent(self, uid):
        self.curs.execute(
            "UPDATE users SET recent = ? WHERE id = ?", ['', uid])
        self.conn.commit()

    def send_otp(self, email):
        try:
            self.curs.execute(
                f"SELECT name from users WHERE email = ?", [email])
            self.name_from_otp = self.curs.fetchone()

            if not self.name_from_otp:
                return 0
            print('hey')
            self.randnumber = randint(100000, 999999)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login("sender_email", "sender_password")
            message = f"Your OTP for PostInter Bank is {str(self.randnumber)}. If not done by you, please report immediately."
            print(message)
            s.sendmail("senderemail", email, message)
            s.quit()

            return 1
        except Exception as e:
            print(e)
            return 0

    def get_details_email(self):
        return self.get_details(self.name_from_otp[0])

    def check_otp(self, otpvalue):
        print(type(self.randnumber), type(otpvalue))
        print(self.randnumber, otpvalue)
        if str(self.randnumber) == str(otpvalue):
            return 1
        else:
            return 0

    def insert_blob(self, blobvalue):
        self.curs.execute(
            f"UPDATE users SET image = ? WHERE id = ?", [blobvalue, self.id])
        self.conn.commit()
        self.curs.execute(
            f"SELECT image FROM users WHERE id = ?", [self.id])
        # print(self.curs.fetchone()[0])
        return self.curs.fetchone()[0]
