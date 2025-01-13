# utils\nextBuilder\backend\smpt_api.py
import tempfile
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8


SMTP_API_CONTENT = """import nodemailer from 'nodemailer';
import crypto from 'crypto';
import db from '../../../../models'; 

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { email } = req.body; // Assume email is passed in the body

    // Generate a secure token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const tokenExpiration = Date.now() + 3600000; // 1 hour from now

    try {
      // Update user with reset token and expiration
      await db.Users.update({
        resetToken: crypto.createHash('sha256').update(resetToken).digest('hex'),
        resetTokenExpiration: tokenExpiration
      }, {
        where: { email: email }
      });

      // SMTP transporter configuration
      let transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST ,
        port: process.env.SMTP_PORT * 1,
        secure: false, // true for 465, false for other ports
        auth: {
          user: SMTP_USER,
          pass: SMTP_PASSWORD,
        },
      });

      // Reset link to be sent via email
      const resetLink = `${process.env.FRONTEND_URL}/auth/password/reset?token=${resetToken}&email=${encodeURIComponent(email)}`;

      // Send mail with defined transport object
      await transporter.sendMail({
        from: '"Flex Data" <support@flexdata.co.za>',
        to: email, 
        subject: "Password Reset", 
        text: `You requested a password reset. Please go to this link to reset your password: ${resetLink}`, 
        html: `<b>Please click on the following link to reset your password:</b> <a href="${resetLink}">Reset Password</a>`,
      });

      return res.status(200).json({ message: "Email sent." });
    } catch (error) {
      console.error("Error sending email", error);
      return res.status(500).json({ error: "Error sending email" });
    }
  } else {
    // Handle any other HTTP method
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
"""


def create_smtp_api():
    subdirectory = "auth/password"  # Define the subdirectory path
    create_api_route('send', SMTP_API_CONTENT, subdirectory)


if __name__ == "__main__":
    create_smtp_api()
