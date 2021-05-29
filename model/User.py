from model.DatabasePool import DatabasePool
from config.Settings import Settings

import datetime
import jwt

import bcrypt

class User:

    @classmethod
    def getUser(cls, user_id):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary = True)
            sql="select * from user where user_id = %s"

            cursor.execute(sql,(user_id, ))
            users = cursor.fetchall() 

            return users

        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def getUserId(cls, email):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary = True)
            sql = "select * from user where email = %s"

            cursor.execute(sql, (email, ))
            users = cursor.fetchall() 

            return users

        finally:
            dbConn.close()
            print("release connection")


    @classmethod
    def getAllUsers(cls):
        dbConn = DatabasePool.getConnection()
        cursor = dbConn.cursor(dictionary = True)
        
        sql="select * from user"
        cursor.execute(sql)
        
        users = cursor.fetchall()

        dbConn.close()

        return users


    @classmethod
    def insertUser(cls, userJson):
        dbConn = DatabasePool.getConnection()
        cursor = dbConn.cursor(dictionary = True)

        sql = "insert into user (user_name, email, role, password) Values (%s, %s, %s, %s)"
        
        users = cursor.execute(sql, (userJson["user_name"], userJson["email"], userJson["role"], userJson["password"]))
        
        dbConn.commit()
        rows=cursor.rowcount
        #print(cursor.lastrowid)

        dbConn.close()

        return rows


# insertUser: store hashed password to sql
#    @classmethod
#    def insertUser(cls, userJson):
#        dbConn = DatabasePool.getConnection()
#        cursor = dbConn.cursor(dictionary = True)

        # Hash a password for the first time, with a randomly-generated salt
#        password = userJson["password"].encode() #convert string to bytes
#        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        
#        sql = "insert into user (user_name, email, role, password) Values (%s, %s, %s, %s)"
        
#        users = cursor.execute(sql, (userJson["user_name"], userJson["email"], userJson["role"], hashed))
        
#        dbConn.commit()
#        rows=cursor.rowcount
        #print(cursor.lastrowid)

#        dbConn.close()

#        return rows


    @classmethod
    def updateUser(cls, user_id, email, password):
        dbConn = DatabasePool.getConnection()
        cursor = dbConn.cursor(dictionary = True)

        sql = "update user set email = %s, password = %s where user_id = %s"
        
        users = cursor.execute(sql, (email, password, user_id))
        
        dbConn.commit()
        rows = cursor.rowcount

        dbConn.close()

        return rows


    @classmethod
    def deleteUser(cls, user_id):
        dbConn=DatabasePool.getConnection()
        cursor = dbConn.cursor(dictionary = True)

        sql="delete from user where user_id = %s"
        
        users = cursor.execute(sql, (user_id,))
        
        dbConn.commit()
        rows=cursor.rowcount

        dbConn.close()

        return rows


    @classmethod
    def loginUser(cls, userJSON):
        try:
            dbConn = DatabasePool.getConnection()
            db_Info = dbConn.connection_id
            print(f"Connected to {db_Info}");

            cursor = dbConn.cursor(dictionary = True)
            
            sql = "select * from user where email = %s and password = %s"

            cursor.execute(sql, (userJSON["email"], userJSON["password"]))
            
            user = cursor.fetchone() #at most 1 record since email is supposed to be unique
     
            if user == None:
                return {"jwt":""}

            else:
                payload={"user_id": user["user_id"], "role": user["role"], "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=7200)}

                jwtToken=jwt.encode(payload, Settings.secretKey, algorithm="HS256")
                return {"jwt":jwtToken}

        finally:
            dbConn.close()


# loginUser: check password against the hashed password
#    @classmethod
#    def loginUser(cls,userJSON):
#        try:
#            dbConn=DatabasePool.getConnection()
            #db_Info = dbConn.connection_id
            #print(f"Connected to {db_Info}");

#            print(userJSON)
#            cursor = dbConn.cursor(dictionary=True)
#            sql="select * from user where email=%s"

#            cursor.execute(sql,(userJSON["email"],))
#            user = cursor.fetchone() #at most 1 record since email is supposed to be unique
#            if user==None:
#                return {"jwt":""}

#            else:
                
#                password=userJSON["password"].encode()
#                hashed=user['password'].encode()
                
#                if bcrypt.checkpw(password, hashed):#True means valid password 
#                    payload={"userid":user["userid"],"role":user["role"],"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=7200)}

#                    jwtToken=jwt.encode(payload,Settings.secretKey,algorithm="HS256")
#                    return {"jwt":jwtToken}
#                else:
#                    return {"jwt":""}
#        finally:
#            dbConn.close()


    @classmethod
    def searchUser(cls, user_name):
        dbConn = DatabasePool.getConnection()
        cursor = dbConn.cursor(dictionary = True)
        
        sql = "select * from user where user_name like %s"
        cursor.execute(sql, ("%"+user_name+"%",))
        
        users = cursor.fetchall()

        dbConn.close()

        return users

