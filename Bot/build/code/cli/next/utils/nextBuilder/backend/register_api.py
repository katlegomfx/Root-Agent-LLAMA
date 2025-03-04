# Bot\build\code\cli\next\utils\nextBuilder\backend\register_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8

# Template for the registration API
REGISTRATION_API_CONTENT = """
import bcrypt from 'bcrypt';
import db from '../../../models';

export default async function register(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).end(`Method ${req.method} Not Allowed`); 
    }

    const { username, email, password } = req.body;

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = await db.Users.create({
            username,
            email,
            password: hashedPassword
        });
        return res.status(201).json({ 
            success: true, 
            message: 'Registration successful', 
            // user: newUser 
        });

    } catch (error) {
        if (error.name === 'SequelizeUniqueConstraintError') {
            return res.status(409).json({ success: false, message: 'User already exists' });
        }
        return res.status(500).json({ success: false, message: error.message});
    }
}
"""

# Use create_api_route to generate the registration API route under the appropriate directory
def create_registration_api():
    # Specify 'auth' as the subdirectory under 'src/pages/api'
    create_api_route('register', REGISTRATION_API_CONTENT, 'auth')

if __name__ == "__main__":
    create_registration_api()
