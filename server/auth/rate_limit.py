import time

class RateLimiter:
    """
    In-memory rate limiter to prevent brute force login attempts and registration spam.
    Tracks requests by IP address.
    """

    LOGIN_MAX_ATTEMPTS = 5
    LOGIN_WINDOW_SEC = 900  # 15 minutes

    REG_MAX_ATTEMPTS = 3
    REG_WINDOW_SEC = 86400  # 24 hours

    def __init__(self):
        self._failed_logins: dict[str, list[float]] = {}
        self._registrations: dict[str, list[float]] = {}
        self._password_resets: dict[str, list[float]] = {}
        self._reset_code_submissions: dict[str, list[float]] = {}
        self._last_full_cleanup = time.time()
        self._cleanup_interval_sec = 300  # Sweep memory every 5 minutes

    def _full_cleanup(self, current_time: float) -> None:
        """Periodic full sweep to prevent memory leaks from single-hit botnet IPs."""
        if current_time - self._last_full_cleanup < self._cleanup_interval_sec:
            return

        # Clean failed logins
        expired_ips = []
        for ip, times in self._failed_logins.items():
            valid_times = [t for t in times if current_time - t <= self.LOGIN_WINDOW_SEC]
            if valid_times:
                self._failed_logins[ip] = valid_times
            else:
                expired_ips.append(ip)
        for ip in expired_ips:
            del self._failed_logins[ip]

        # Clean registrations
        expired_ips = []
        for ip, times in self._registrations.items():
            valid_times = [t for t in times if current_time - t <= self.REG_WINDOW_SEC]
            if valid_times:
                self._registrations[ip] = valid_times
            else:
                expired_ips.append(ip)
        for ip in expired_ips:
            del self._registrations[ip]

        # Clean password resets
        expired_ips = []
        for ip, times in self._password_resets.items():
            valid_times = [t for t in times if current_time - t <= 900]
            if valid_times:
                self._password_resets[ip] = valid_times
            else:
                expired_ips.append(ip)
        for ip in expired_ips:
            del self._password_resets[ip]

        # Clean reset code submissions
        expired_ips = []
        for ip, times in self._reset_code_submissions.items():
            valid_times = [t for t in times if current_time - t <= 900]
            if valid_times:
                self._reset_code_submissions[ip] = valid_times
            else:
                expired_ips.append(ip)
        for ip in expired_ips:
            del self._reset_code_submissions[ip]

        self._last_full_cleanup = current_time

    def _cleanup_list(self, ip: str, data_dict: dict[str, list[float]], window: int) -> list[float]:
        """Lazy cleanup of expired timestamps for a given IP."""
        current_time = time.time()
        self._full_cleanup(current_time)

        if ip not in data_dict:
            return []

        # Keep only timestamps within the window
        valid_times = [t for t in data_dict[ip] if current_time - t <= window]

        if not valid_times:
            # Completely remove the key to prevent memory leaks over long uptimes
            del data_dict[ip]
        else:
            data_dict[ip] = valid_times

        return valid_times

    def is_login_allowed(self, ip: str) -> bool:
        """Check if an IP is allowed to attempt a login."""
        valid_times = self._cleanup_list(ip, self._failed_logins, self.LOGIN_WINDOW_SEC)
        return len(valid_times) < self.LOGIN_MAX_ATTEMPTS

    def record_failed_login(self, ip: str) -> None:
        """Record a failed login attempt for an IP."""
        if ip not in self._failed_logins:
            self._failed_logins[ip] = []
        self._failed_logins[ip].append(time.time())
        # Force a cleanup immediately to prevent unbounded list growth per IP
        self._cleanup_list(ip, self._failed_logins, self.LOGIN_WINDOW_SEC)

    def clear_failed_logins(self, ip: str) -> None:
        """Clear failed login attempts for an IP (e.g. after a successful login)."""
        if ip in self._failed_logins:
            del self._failed_logins[ip]

    def is_password_reset_allowed(self, ip: str) -> bool:
        """Check if a password reset request is allowed for this IP (Max 2 per 15 min)."""
        valid_times = self._cleanup_list(ip, self._password_resets, 900)
        return len(valid_times) < 2

    def record_password_reset(self, ip: str) -> None:
        """Record a password reset request attempt."""
        if ip not in self._password_resets:
            self._password_resets[ip] = []
        self._password_resets[ip].append(time.time())
        self._cleanup_list(ip, self._password_resets, 900)

    def is_reset_code_submission_allowed(self, ip: str) -> bool:
        """Check if submitting a reset code is allowed for this IP (Max 5 per 15 min)."""
        valid_times = self._cleanup_list(ip, self._reset_code_submissions, 900)
        return len(valid_times) < 5

    def record_reset_code_submission(self, ip: str) -> None:
        """Record a failed reset code submission attempt."""
        if ip not in self._reset_code_submissions:
            self._reset_code_submissions[ip] = []
        self._reset_code_submissions[ip].append(time.time())
        self._cleanup_list(ip, self._reset_code_submissions, 900)

    def clear_reset_code_submissions(self, ip: str) -> None:
        """Clear failed reset code submission attempts for an IP."""
        if ip in self._reset_code_submissions:
            del self._reset_code_submissions[ip]

    def is_registration_allowed(self, ip: str) -> bool:
        """Check if an IP is allowed to register a new account."""
        valid_times = self._cleanup_list(ip, self._registrations, self.REG_WINDOW_SEC)
        return len(valid_times) < self.REG_MAX_ATTEMPTS

    def record_registration(self, ip: str) -> None:
        """Record a successful registration for an IP."""
        if ip not in self._registrations:
            self._registrations[ip] = []
        self._registrations[ip].append(time.time())
        self._cleanup_list(ip, self._registrations, self.REG_WINDOW_SEC)
