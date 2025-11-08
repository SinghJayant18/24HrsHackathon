# Registration Guide - Input Format Rules & Examples

## 📋 Required Fields (Must Fill)

### 1. **Full Name**
- **Format**: Any text, 2-200 characters
- **Example**: `Ram Singh`
- **Rules**: 
  - No special characters required
  - Can include spaces

### 2. **Email Address**
- **Format**: Valid email format
- **Example**: `singhjayant1805@gmail.com`
- **Rules**:
  - Must be a valid email
  - Must be unique (not already registered)

### 3. **Password**
- **Format**: Minimum 6 characters, maximum 72 characters
- **Example**: `MySecurePass123`
- **Rules**:
  - At least 6 characters long
  - Can include letters, numbers, and special characters
  - Maximum 72 characters

### 4. **Contact Number**
- **Format**: Exactly 10 digits
- **Example**: `8829843181`
- **Rules**:
  - Only digits (0-9)
  - Exactly 10 digits
  - Spaces and dashes are automatically removed
  - **Correct**: `8829843181` or `8829 843 181` or `8829-843-181`
  - **Wrong**: `882984318` (9 digits) or `88298431811` (11 digits)

### 5. **PAN Card Number**
- **Format**: Exactly 10 characters - 5 letters + 4 digits + 1 letter
- **Example**: `ABCDE1234F`
- **Rules**:
  - First 5 characters must be letters (A-Z)
  - Next 4 characters must be digits (0-9)
  - Last 1 character must be a letter (A-Z)
  - Automatically converted to uppercase
  - Must be unique (not already registered)
  - **Correct**: `ABCDE1234F`, `PANCD5678K`
  - **Wrong**: `ABCD1234` (9 chars), `ABCD12345F` (11 chars), `1234ABCDEF` (wrong format)

---

## 📝 Optional Fields (Can Skip)

### 6. **Aadhar Number**
- **Format**: Exactly 12 digits
- **Example**: `123456789012`
- **Rules**:
  - Only digits (0-9)
  - Exactly 12 digits
  - Spaces and dashes are automatically removed
  - **Correct**: `123456789012` or `1234 5678 9012`
  - **Wrong**: `12345678901` (11 digits) or `1234567890123` (13 digits)

### 7. **Business Name**
- **Format**: Any text
- **Example**: `KIRANA` or `Ram Singh General Store`
- **Rules**: No specific format required

### 8. **Business Address**
- **Format**: Any text
- **Example**: `Malaviya National Institute of Technology, Jaipur, Rajasthan`
- **Rules**: No specific format required

### 9. **GST Number**
- **Format**: Exactly 15 characters
- **Example**: `29ABCDE1234F1Z5`
- **Rules**:
  - Exactly 15 characters
  - Automatically converted to uppercase
  - **Correct**: `29ABCDE1234F1Z5`
  - **Wrong**: `29ABCDE1234F1Z` (14 chars) or `29ABCDE1234F1Z56` (16 chars)

### 10. **Bank Account Number**
- **Format**: Any alphanumeric
- **Example**: `6749925343` or `6749925343F`
- **Rules**: No specific format required

### 11. **IFSC Code**
- **Format**: Exactly 11 characters - 4 letters + 7 digits
- **Example**: `SBIN0001234`
- **Rules**:
  - First 4 characters must be letters (A-Z)
  - Next 7 characters must be digits (0-9)
  - Automatically converted to uppercase
  - **Correct**: `SBIN0001234`, `HDFC0001234`
  - **Wrong**: `SBIN001234` (10 chars), `SBIN00012345` (12 chars), `1234SBIN000` (wrong format)

---

## ✅ Complete Registration Example

Here's a complete example with all fields filled correctly:

```
Full Name: Ram Singh
Email Address: singhjayant1805@gmail.com
Password: MySecurePass123
Contact Number: 8829843181
PAN Card Number: ABCDE1234F

Aadhar Number: 123456789012
Business Name: KIRANA
Business Address: Malaviya National Institute of Technology, Jaipur, Rajasthan
GST Number: 29ABCDE1234F1Z5
Bank Account Number: 6749925343
IFSC Code: SBIN0001234
```

---

## ❌ Common Mistakes to Avoid

1. **PAN Card**: 
   - ❌ `ABCD1234` (too short)
   - ❌ `ABCD12345F` (too long)
   - ❌ `1234ABCDEF` (wrong format - numbers first)
   - ✅ `ABCDE1234F` (correct)

2. **Contact Number**:
   - ❌ `882984318` (9 digits)
   - ❌ `88298431811` (11 digits)
   - ❌ `8829843181a` (contains letter)
   - ✅ `8829843181` (correct)

3. **IFSC Code**:
   - ❌ `SBIN001234` (10 chars)
   - ❌ `1234SBIN000` (wrong format)
   - ✅ `SBIN0001234` (correct)

4. **Password**:
   - ❌ `pass` (too short - less than 6)
   - ✅ `MyPass123` (correct - 9 characters)

---

## 🔍 Validation Summary

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| Full Name | ✅ Yes | 2-200 chars | `Ram Singh` |
| Email | ✅ Yes | Valid email | `user@example.com` |
| Password | ✅ Yes | 6-72 chars | `MyPass123` |
| Contact | ✅ Yes | 10 digits | `8829843181` |
| PAN Card | ✅ Yes | 10 chars (5L+4D+1L) | `ABCDE1234F` |
| Aadhar | ❌ No | 12 digits | `123456789012` |
| Business Name | ❌ No | Any text | `KIRANA` |
| Business Address | ❌ No | Any text | `Address here` |
| GST Number | ❌ No | 15 chars | `29ABCDE1234F1Z5` |
| Bank Account | ❌ No | Any text | `6749925343` |
| IFSC Code | ❌ No | 11 chars (4L+7D) | `SBIN0001234` |

---

## 💡 Tips

1. **All text fields are automatically trimmed** (spaces removed from start/end)
2. **PAN, IFSC, and GST are automatically converted to UPPERCASE**
3. **Contact and Aadhar automatically remove spaces and dashes**
4. **If you get an error, check the format carefully**
5. **Email and PAN must be unique** - if already registered, use different values

---

**Need Help?** Check the error message - it will tell you exactly what's wrong with your input!

