EduOne Missing Pages Patch

This patch supplies the missing Syllabus, Profile, Resources, PYQ, Quiz,
and Question Scanner result templates, plus Resources/PYQ/Quiz URL/view files.

HOW TO INSTALL
1. Stop the Django server only if you need to; template changes can usually
   be picked up automatically.
2. Copy the contents of this ZIP into the EduOne project root:
   C:\Users\aksha\.gemini\antigravity\scratch\eduone\
3. Allow Windows/VS Code to merge the files and replace the existing
   resources/urls.py, pyqs/urls.py, and quizzes/urls.py.
4. In the terminal, run:
      python manage.py check
5. Start/restart Django:
      python manage.py runserver
6. Test:
      /academics/syllabus/
      /resources/notes/
      /resources/videos/
      /pyqs/
      /pyqs/important/
      /quizzes/
      /accounts/profile/

IMPORTANT
- This patch does not contain your .env or API key.
- Do not upload/share your .env.
- The Gemini model/SDK change is separate from these missing-page fixes.
