from enum import Enum


class UserRoleSchema(str, Enum):
    superadmin = 'Super Admin'
    admin = 'Admin'
    student = 'Student'
    general = 'General'


class UniversitySchema(str, Enum):
    test = 'test'
    test_university = "Test University"
