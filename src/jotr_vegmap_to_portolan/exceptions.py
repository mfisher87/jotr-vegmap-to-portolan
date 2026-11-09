class TypeguardException(RuntimeError):
    def __init__(self) -> None:
        self.message = "This is a typeguard; if this raises at runtime you gots a bug"
        super().__init__(self.message)
