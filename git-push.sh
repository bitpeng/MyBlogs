#!/usr/bin/expect

spawn git push -u origin master

expect  "Username"
send "bitpeng@yeah.net\r"

expect  "Password"
send "ab193777\r"

expect eof
interact
