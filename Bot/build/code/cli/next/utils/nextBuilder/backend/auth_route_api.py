# Bot\build\code\cli\next\utils\nextBuilder\backend\auth_route_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8

# Template for the NextAuth route
nextAuthJSContent = """import NextAuth from "next-auth"
import CredentialProvider from "next-auth/providers/credentials"

export default NextAuth({
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    CredentialProvider({
      id: "credential",
      name: "credential",
      credentials: {
        email: '',
        password: '',
        type: '',
        remember: '',
        username: '',
        name: '',
        surname: '',
      },
      async authorize(credentials, req) {
        try {
          if (credentials.type === 'login') {
            let sendUsername = credentials.username;
            let sendPassword = credentials.password;
            let url = `${process.env.NEXTAUTH_URL}api/auth/login`
            const data = await fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'username': sendUsername, 'password': sendPassword }),
            });
            const final = await data.json();
            if (final.success) {
              return {
                username: sendUsername,
                info: final.user,
                token: final.token
              };
            }
            if (!final.success) {
              return
            }
          } else {
            let sendUsername = credentials.username;
            let sendEmail = credentials.email;
            let sendPassword = credentials.password;
            let url = `${process.env.NEXTAUTH_URL}api/auth/register`
            const data = await fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'username': sendUsername, 'email': sendEmail, 'password': sendPassword }),
            });
            const final = await data.json();
            if (final.success) {
              return final
            }
            if (!final.success) {
              return
            }
          }
        } catch (error) {
          console.log(error)
        }
      }
    }),
  ],
  callbacks: {
    // redirect: async ({ url, baseUrl }) => {
    //   // Allows relative callback URLs
    //   if (url.startsWith("/")) return `${baseUrl}${url}`
    //   // Allows callback URLs on the same origin
    //   else if (new URL(url).origin === baseUrl) return url
    //   return baseUrl
    // },
    jwt: async ({ token, user }) => {
      user && (token.user = user);
      return token;
    },
    session: async ({ session, token }) => {
      if (!session.user.message) {
        session.user = token.user;
        return session;
      } else {
        return
      }
    },
  },
  pages: {
    signIn: "/auth/login",
    signUp: "/auth/register",
  },
  session: {
    maxAge: 60 * 10
  },
})
"""

def create_nextauth_configuration():
    name = '[...nextauth]'
    create_api_route(name, nextAuthJSContent, 'auth')

if __name__ == "__main__":
    create_nextauth_configuration()
