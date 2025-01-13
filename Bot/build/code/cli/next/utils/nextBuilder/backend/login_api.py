# utils\nextBuilder\backend\login_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8

# Template for the login API
LOGIN_API_CONTENT = """
import db from '../../../models';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

export default async function login(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).end(`Method ${req.method} Not Allowed`);
    }

    const { username, password } = req.body;

    try {
        const user = await db.Users.findOne({ where: { username } });
        if (user && bcrypt.compareSync(password, user.password)) { 
            const token = jwt.sign(
                { userId: user.id, username: user.username },
                process.env.JWT_SECRET, 
                { expiresIn: '1h' } 
            );
            return res.status(200).json({ success: true, message: 'Login successful', token, user });
        } else {
            return res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
    } catch (error) {
        return res.status(500).json({ success: false, message: error.message });
    }
}
"""


# Use create_api_route to generate the login.js file under the specified directory
def create_login_api():
    # 'auth' is the subdirectory under 'src/pages/api'
    create_api_route('login', LOGIN_API_CONTENT, 'auth')


if __name__ == "__main__":
    create_login_api()
