

# CCS Sitin Monitoring System

A Django-based web application for monitoring and managing computer lab sessions at a college level. The system allows students to reserve PCs, sit in during available sessions, receive rewards, and stay updated via announcements. Admins manage reservations, sessions, and generate reports through a dedicated interface.



---



## 🚀 Features

- **🔔 Real-time Notifications** using WebSockets
- **🗣️ Announcement System** with comment, edit, and delete functionalities
- **🖥️ Computer Reservation System** for lab PCs
- **📥 Sit-in Requests** — students can request admins to sit them in without reserving
- **⏳ Session-Based Sitin** — students can sit in as long as a session is active
- **🏅 Rewards & Leaderboards** — admins reward active students based on performance
- **📄 Pagination** for fast content loading and display
- **👤 Profile Management System** to customize user profiles
- **🛠️ Admin Dashboard** via Django Admin for full management control



---



## 🛠️ Installation (Development)

Make sure you have **Python**, **Git**, and your preferred **IDE** installed.

```bash
git clone https://github.com/VulpritProoze/sysarch001_alin.git
cd sysarch001_alin
pip install virtualenv
virtualenv venv
venv\Scripts\activate    # For Windows (use `source venv/bin/activate` on macOS/Linux)
pip install -r requirements.txt
cd app
python manage.py runserver
````

Then open the app at: [http://localhost:5006](http://localhost:5006)



---



## 💡 Usage Examples

1. **Dashboard**: Displays lab rules and latest announcements.

  ![image](https://github.com/user-attachments/assets/e01931b3-d178-4d31-83eb-4127f0b17abd)
  ![image](https://github.com/user-attachments/assets/a0b37911-7d02-4421-915b-61ac497d3cef)

2. **Announcements**: View, comment, edit, and delete announcements.

  ![image](https://github.com/user-attachments/assets/65b26028-3add-478e-bfd2-9a20fc8d3e20)
  ![image](https://github.com/user-attachments/assets/0b6073fc-f7cb-4a59-a0d4-b29b85e799a8)


3. **Reservations**:

   * Navigate to a lab room.
   * Click the action button of an available PC.
   * Wait for admin approval.
   * Admin logs out the student manually in `/admin/`.

  ![image](https://github.com/user-attachments/assets/b4d112ac-235e-4e2f-8e2d-78cf706e0c53)
  ![image](https://github.com/user-attachments/assets/6e1ee7d0-3175-4846-9626-4d870199d083)
  ![image](https://github.com/user-attachments/assets/2d9255d0-44c0-4736-84d2-5a24462b721c)


4. **Sitin History**: Students can review previous sitins and give feedback.
  
  ![image](https://github.com/user-attachments/assets/8e796679-7bad-4c30-9ed6-6d224f0529bb)

5. **Resources**: Students can access educational files shared by admins, and upload their own lab schedules (their study load).

  ![image](https://github.com/user-attachments/assets/3ac67065-425f-4e9a-9e84-12a782458c6e)
  ![image](https://github.com/user-attachments/assets/83ec8202-0590-40f7-a5e1-d0d5dfeeb6a7)

6. **Admin Page**: Administrators can browse through various tools to monitor student activity.

  ![image](https://github.com/user-attachments/assets/5ef311e1-8c0e-4a1c-99d5-12ef504e19c2)
  ![image](https://github.com/user-attachments/assets/2053fbd4-fce5-4e63-a209-fc640a6ab242)



---



## 👥 User Modes

* **Student/User**: Accessible at `/`
* **Admin**: Accessible via Django Admin panel at `/admin/`



---



## 🤝 Contributing Guidelines

We welcome contributions to improve the CCS Sitin Monitoring System! To contribute:

1. **Fork** the repository to your own GitHub account.
2. **Clone** your forked repo to your local machine:

   ```bash
   git clone https://github.com/your-username/sysarch001_alin.git
   ```
3. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**, following the existing code style and structure.
5. **Test your changes** thoroughly before committing.
6. **Commit and push** your changes to your fork:

   ```bash
   git add .
   git commit -m "Add: Your detailed commit message"
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** from your branch to the `main` branch of this repository. Clearly describe:

   * What the change does
   * Why it's needed
   * Any additional context or dependencies

Please ensure your code:

* Is well-documented
* Does not introduce breaking changes
* Has been tested for bugs and regressions

We appreciate clean, respectful collaboration!
