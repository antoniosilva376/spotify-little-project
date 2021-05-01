from auxiliares import checkCommonSongsHTML
from auxiliares import dividePlaylists

client_token = ''
secret_token = ''

def menu():
    print("\nSheesh\n")
    
    opc = 1
    while opc:
        opc = int( input("1. Insert client/secret token (do this first)\n2. Divide playlist by song year.\n3. Compare playlists\n\n") )
        if (opc<0 or opc >3):
            print("Incorrect!") 
        else:
            if opc == 1:
                client_token = "client_token = '" + input("\nInsert client token\n")
                secret_token = "'\nsecret_token = '" + input("\nInsert secret token\n") + "'"
                file = open("secrets.py","w")
                file.write(client_token + secret_token)
                file.close()
                pass

            elif opc == 2:
                uri = input("\nInsert URI from playlist\n")
                user = input("\nInsert user URI from playlist\n")
                year = input("\nInsert year\n")
                name_A = input("\nInsert under (<) year playlist name\n")
                name_B = input("\nInsert over (>=) year playlist name\n")
                dividePlaylists(client_token,secret_token,uri,user,name_A,name_B,year)
                print("\nPlaylist created!\n")
                pass

            elif opc == 3:
                uri_A = input("\nInsert URI from first playlist\n")
                user_A = input("\nInsert user URI from first playlist\n")
                uri_B = input("\nInsert URI from second playlist\n")
                user_B = input("\nInsert user URI from second playlist\n")
                checkCommonSongsHTML(client_token,secret_token,uri_A,user_A,uri_B,user_B)
                print("\nHTML created!\n")
                pass

menu()