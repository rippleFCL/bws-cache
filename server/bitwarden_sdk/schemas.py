from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List, Dict, TypeVar, Type, cast, Callable
from uuid import UUID
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


class DeviceType(Enum):
    """Device type to send to Bitwarden. Defaults to SDK"""
    ANDROID = "Android"
    ANDROID_AMAZON = "AndroidAmazon"
    CHROME_BROWSER = "ChromeBrowser"
    CHROME_EXTENSION = "ChromeExtension"
    EDGE_BROWSER = "EdgeBrowser"
    EDGE_EXTENSION = "EdgeExtension"
    FIREFOX_BROWSER = "FirefoxBrowser"
    FIREFOX_EXTENSION = "FirefoxExtension"
    IE_BROWSER = "IEBrowser"
    I_OS = "iOS"
    LINUX_DESKTOP = "LinuxDesktop"
    MAC_OS_DESKTOP = "MacOsDesktop"
    OPERA_BROWSER = "OperaBrowser"
    OPERA_EXTENSION = "OperaExtension"
    SAFARI_BROWSER = "SafariBrowser"
    SAFARI_EXTENSION = "SafariExtension"
    SDK = "SDK"
    UNKNOWN_BROWSER = "UnknownBrowser"
    UWP = "UWP"
    VIVALDI_BROWSER = "VivaldiBrowser"
    VIVALDI_EXTENSION = "VivaldiExtension"
    WINDOWS_DESKTOP = "WindowsDesktop"


@dataclass
class ClientSettings:
    """Basic client behavior settings. These settings specify the various targets and behavior
    of the Bitwarden Client. They are optional and uneditable once the client is
    initialized.
    
    Defaults to
    
    ``` # use bitwarden::client::client_settings::{ClientSettings, DeviceType}; let settings
    = ClientSettings { identity_url: "https://identity.bitwarden.com".to_string(), api_url:
    "https://api.bitwarden.com".to_string(), user_agent: "Bitwarden Rust-SDK".to_string(),
    device_type: DeviceType::SDK, }; let default = ClientSettings::default(); ```
    """
    api_url: Optional[str] = None
    """The api url of the targeted Bitwarden instance. Defaults to `https://api.bitwarden.com`"""
    device_type: Optional[DeviceType] = None
    """Device type to send to Bitwarden. Defaults to SDK"""
    identity_url: Optional[str] = None
    """The identity url of the targeted Bitwarden instance. Defaults to
    `https://identity.bitwarden.com`
    """
    user_agent: Optional[str] = None
    """The user_agent to sent to Bitwarden. Defaults to `Bitwarden Rust-SDK`"""

    @staticmethod
    def from_dict(obj: Any) -> 'ClientSettings':
        assert isinstance(obj, dict)
        api_url = from_union([from_str, from_none], obj.get("apiUrl"))
        device_type = from_union([DeviceType, from_none], obj.get("deviceType"))
        identity_url = from_union([from_str, from_none], obj.get("identityUrl"))
        user_agent = from_union([from_str, from_none], obj.get("userAgent"))
        return ClientSettings(api_url, device_type, identity_url, user_agent)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.api_url is not None:
            result["apiUrl"] = from_union([from_str, from_none], self.api_url)
        if self.device_type is not None:
            result["deviceType"] = from_union([lambda x: to_enum(DeviceType, x), from_none], self.device_type)
        if self.identity_url is not None:
            result["identityUrl"] = from_union([from_str, from_none], self.identity_url)
        if self.user_agent is not None:
            result["userAgent"] = from_union([from_str, from_none], self.user_agent)
        return result


@dataclass
class AccessTokenLoginRequest:
    """Login to Bitwarden with access token"""
    access_token: str
    """Bitwarden service API access token"""
    state_file: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AccessTokenLoginRequest':
        assert isinstance(obj, dict)
        access_token = from_str(obj.get("accessToken"))
        state_file = from_union([from_none, from_str], obj.get("stateFile"))
        return AccessTokenLoginRequest(access_token, state_file)

    def to_dict(self) -> dict:
        result: dict = {}
        result["accessToken"] = from_str(self.access_token)
        if self.state_file is not None:
            result["stateFile"] = from_union([from_none, from_str], self.state_file)
        return result


@dataclass
class APIKeyLoginRequest:
    """Login to Bitwarden with Api Key"""
    client_id: str
    """Bitwarden account client_id"""
    client_secret: str
    """Bitwarden account client_secret"""
    password: str
    """Bitwarden account master password"""

    @staticmethod
    def from_dict(obj: Any) -> 'APIKeyLoginRequest':
        assert isinstance(obj, dict)
        client_id = from_str(obj.get("clientId"))
        client_secret = from_str(obj.get("clientSecret"))
        password = from_str(obj.get("password"))
        return APIKeyLoginRequest(client_id, client_secret, password)

    def to_dict(self) -> dict:
        result: dict = {}
        result["clientId"] = from_str(self.client_id)
        result["clientSecret"] = from_str(self.client_secret)
        result["password"] = from_str(self.password)
        return result


@dataclass
class FingerprintRequest:
    fingerprint_material: str
    """The input material, used in the fingerprint generation process."""
    public_key: str
    """The user's public key encoded with base64."""

    @staticmethod
    def from_dict(obj: Any) -> 'FingerprintRequest':
        assert isinstance(obj, dict)
        fingerprint_material = from_str(obj.get("fingerprintMaterial"))
        public_key = from_str(obj.get("publicKey"))
        return FingerprintRequest(fingerprint_material, public_key)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fingerprintMaterial"] = from_str(self.fingerprint_material)
        result["publicKey"] = from_str(self.public_key)
        return result


@dataclass
class SecretVerificationRequest:
    master_password: Optional[str] = None
    """The user's master password to use for user verification. If supplied, this will be used
    for verification purposes.
    """
    otp: Optional[str] = None
    """Alternate user verification method through OTP. This is provided for users who have no
    master password due to use of Customer Managed Encryption. Must be present and valid if
    master_password is absent.
    """

    @staticmethod
    def from_dict(obj: Any) -> 'SecretVerificationRequest':
        assert isinstance(obj, dict)
        master_password = from_union([from_none, from_str], obj.get("masterPassword"))
        otp = from_union([from_none, from_str], obj.get("otp"))
        return SecretVerificationRequest(master_password, otp)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.master_password is not None:
            result["masterPassword"] = from_union([from_none, from_str], self.master_password)
        if self.otp is not None:
            result["otp"] = from_union([from_none, from_str], self.otp)
        return result


@dataclass
class Argon2ID:
    iterations: int
    memory: int
    parallelism: int

    @staticmethod
    def from_dict(obj: Any) -> 'Argon2ID':
        assert isinstance(obj, dict)
        iterations = from_int(obj.get("iterations"))
        memory = from_int(obj.get("memory"))
        parallelism = from_int(obj.get("parallelism"))
        return Argon2ID(iterations, memory, parallelism)

    def to_dict(self) -> dict:
        result: dict = {}
        result["iterations"] = from_int(self.iterations)
        result["memory"] = from_int(self.memory)
        result["parallelism"] = from_int(self.parallelism)
        return result


@dataclass
class PBKDF2:
    iterations: int

    @staticmethod
    def from_dict(obj: Any) -> 'PBKDF2':
        assert isinstance(obj, dict)
        iterations = from_int(obj.get("iterations"))
        return PBKDF2(iterations)

    def to_dict(self) -> dict:
        result: dict = {}
        result["iterations"] = from_int(self.iterations)
        return result


@dataclass
class Kdf:
    """Kdf from prelogin"""
    p_bkdf2: Optional[PBKDF2] = None
    argon2_id: Optional[Argon2ID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Kdf':
        assert isinstance(obj, dict)
        p_bkdf2 = from_union([PBKDF2.from_dict, from_none], obj.get("pBKDF2"))
        argon2_id = from_union([Argon2ID.from_dict, from_none], obj.get("argon2id"))
        return Kdf(p_bkdf2, argon2_id)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.p_bkdf2 is not None:
            result["pBKDF2"] = from_union([lambda x: to_class(PBKDF2, x), from_none], self.p_bkdf2)
        if self.argon2_id is not None:
            result["argon2id"] = from_union([lambda x: to_class(Argon2ID, x), from_none], self.argon2_id)
        return result


class TwoFactorProvider(Enum):
    """Two-factor provider"""
    AUTHENTICATOR = "Authenticator"
    DUO = "Duo"
    EMAIL = "Email"
    ORGANIZATION_DUO = "OrganizationDuo"
    REMEMBER = "Remember"
    U2_F = "U2f"
    WEB_AUTHN = "WebAuthn"
    YUBIKEY = "Yubikey"


@dataclass
class TwoFactorRequest:
    provider: TwoFactorProvider
    """Two-factor provider"""
    remember: bool
    """Two-factor remember"""
    token: str
    """Two-factor Token"""

    @staticmethod
    def from_dict(obj: Any) -> 'TwoFactorRequest':
        assert isinstance(obj, dict)
        provider = TwoFactorProvider(obj.get("provider"))
        remember = from_bool(obj.get("remember"))
        token = from_str(obj.get("token"))
        return TwoFactorRequest(provider, remember, token)

    def to_dict(self) -> dict:
        result: dict = {}
        result["provider"] = to_enum(TwoFactorProvider, self.provider)
        result["remember"] = from_bool(self.remember)
        result["token"] = from_str(self.token)
        return result


@dataclass
class PasswordLoginRequest:
    """Login to Bitwarden with Username and Password"""
    email: str
    """Bitwarden account email address"""
    kdf: Kdf
    """Kdf from prelogin"""
    password: str
    """Bitwarden account master password"""
    two_factor: Optional[TwoFactorRequest] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PasswordLoginRequest':
        assert isinstance(obj, dict)
        email = from_str(obj.get("email"))
        kdf = Kdf.from_dict(obj.get("kdf"))
        password = from_str(obj.get("password"))
        two_factor = from_union([TwoFactorRequest.from_dict, from_none], obj.get("twoFactor"))
        return PasswordLoginRequest(email, kdf, password, two_factor)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_str(self.email)
        result["kdf"] = to_class(Kdf, self.kdf)
        result["password"] = from_str(self.password)
        if self.two_factor is not None:
            result["twoFactor"] = from_union([lambda x: to_class(TwoFactorRequest, x), from_none], self.two_factor)
        return result


@dataclass
class ProjectCreateRequest:
    name: str
    organization_id: UUID
    """Organization where the project will be created"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectCreateRequest':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        organization_id = UUID(obj.get("organizationId"))
        return ProjectCreateRequest(name, organization_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["organizationId"] = str(self.organization_id)
        return result


@dataclass
class ProjectsDeleteRequest:
    ids: List[UUID]
    """IDs of the projects to delete"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectsDeleteRequest':
        assert isinstance(obj, dict)
        ids = from_list(lambda x: UUID(x), obj.get("ids"))
        return ProjectsDeleteRequest(ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ids"] = from_list(lambda x: str(x), self.ids)
        return result


@dataclass
class ProjectGetRequest:
    id: UUID
    """ID of the project to retrieve"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectGetRequest':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        return ProjectGetRequest(id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        return result


@dataclass
class ProjectsListRequest:
    organization_id: UUID
    """Organization to retrieve all the projects from"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectsListRequest':
        assert isinstance(obj, dict)
        organization_id = UUID(obj.get("organizationId"))
        return ProjectsListRequest(organization_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["organizationId"] = str(self.organization_id)
        return result


@dataclass
class ProjectPutRequest:
    id: UUID
    """ID of the project to modify"""
    name: str
    organization_id: UUID
    """Organization ID of the project to modify"""

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectPutRequest':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        name = from_str(obj.get("name"))
        organization_id = UUID(obj.get("organizationId"))
        return ProjectPutRequest(id, name, organization_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        result["name"] = from_str(self.name)
        result["organizationId"] = str(self.organization_id)
        return result


@dataclass
class ProjectsCommand:
    """> Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Retrieve a project by the provided identifier
    
    Returns: [ProjectResponse](bitwarden::secrets_manager::projects::ProjectResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Creates a new project in the provided organization using the given data
    
    Returns: [ProjectResponse](bitwarden::secrets_manager::projects::ProjectResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Lists all projects of the given organization
    
    Returns: [ProjectsResponse](bitwarden::secrets_manager::projects::ProjectsResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Updates an existing project with the provided ID using the given data
    
    Returns: [ProjectResponse](bitwarden::secrets_manager::projects::ProjectResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Deletes all the projects whose IDs match the provided ones
    
    Returns:
    [ProjectsDeleteResponse](bitwarden::secrets_manager::projects::ProjectsDeleteResponse)
    """
    get: Optional[ProjectGetRequest] = None
    create: Optional[ProjectCreateRequest] = None
    list: Optional[ProjectsListRequest] = None
    update: Optional[ProjectPutRequest] = None
    delete: Optional[ProjectsDeleteRequest] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectsCommand':
        assert isinstance(obj, dict)
        get = from_union([ProjectGetRequest.from_dict, from_none], obj.get("get"))
        create = from_union([ProjectCreateRequest.from_dict, from_none], obj.get("create"))
        list = from_union([ProjectsListRequest.from_dict, from_none], obj.get("list"))
        update = from_union([ProjectPutRequest.from_dict, from_none], obj.get("update"))
        delete = from_union([ProjectsDeleteRequest.from_dict, from_none], obj.get("delete"))
        return ProjectsCommand(get, create, list, update, delete)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.get is not None:
            result["get"] = from_union([lambda x: to_class(ProjectGetRequest, x), from_none], self.get)
        if self.create is not None:
            result["create"] = from_union([lambda x: to_class(ProjectCreateRequest, x), from_none], self.create)
        if self.list is not None:
            result["list"] = from_union([lambda x: to_class(ProjectsListRequest, x), from_none], self.list)
        if self.update is not None:
            result["update"] = from_union([lambda x: to_class(ProjectPutRequest, x), from_none], self.update)
        if self.delete is not None:
            result["delete"] = from_union([lambda x: to_class(ProjectsDeleteRequest, x), from_none], self.delete)
        return result


@dataclass
class SecretCreateRequest:
    key: str
    note: str
    organization_id: UUID
    """Organization where the secret will be created"""
    value: str
    project_ids: Optional[List[UUID]] = None
    """IDs of the projects that this secret will belong to"""

    @staticmethod
    def from_dict(obj: Any) -> 'SecretCreateRequest':
        assert isinstance(obj, dict)
        key = from_str(obj.get("key"))
        note = from_str(obj.get("note"))
        organization_id = UUID(obj.get("organizationId"))
        value = from_str(obj.get("value"))
        project_ids = from_union([from_none, lambda x: from_list(lambda x: UUID(x), x)], obj.get("projectIds"))
        return SecretCreateRequest(key, note, organization_id, value, project_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["key"] = from_str(self.key)
        result["note"] = from_str(self.note)
        result["organizationId"] = str(self.organization_id)
        result["value"] = from_str(self.value)
        if self.project_ids is not None:
            result["projectIds"] = from_union([from_none, lambda x: from_list(lambda x: str(x), x)], self.project_ids)
        return result


@dataclass
class SecretsDeleteRequest:
    ids: List[UUID]
    """IDs of the secrets to delete"""

    @staticmethod
    def from_dict(obj: Any) -> 'SecretsDeleteRequest':
        assert isinstance(obj, dict)
        ids = from_list(lambda x: UUID(x), obj.get("ids"))
        return SecretsDeleteRequest(ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ids"] = from_list(lambda x: str(x), self.ids)
        return result


@dataclass
class SecretGetRequest:
    id: UUID
    """ID of the secret to retrieve"""

    @staticmethod
    def from_dict(obj: Any) -> 'SecretGetRequest':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        return SecretGetRequest(id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        return result


@dataclass
class SecretsGetRequest:
    ids: List[UUID]
    """IDs of the secrets to retrieve"""

    @staticmethod
    def from_dict(obj: Any) -> 'SecretsGetRequest':
        assert isinstance(obj, dict)
        ids = from_list(lambda x: UUID(x), obj.get("ids"))
        return SecretsGetRequest(ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ids"] = from_list(lambda x: str(x), self.ids)
        return result


@dataclass
class SecretIdentifiersRequest:
    organization_id: UUID
    """Organization to retrieve all the secrets from"""

    @staticmethod
    def from_dict(obj: Any) -> 'SecretIdentifiersRequest':
        assert isinstance(obj, dict)
        organization_id = UUID(obj.get("organizationId"))
        return SecretIdentifiersRequest(organization_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["organizationId"] = str(self.organization_id)
        return result


@dataclass
class SecretPutRequest:
    id: UUID
    """ID of the secret to modify"""
    key: str
    note: str
    organization_id: UUID
    """Organization ID of the secret to modify"""
    value: str
    project_ids: Optional[List[UUID]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SecretPutRequest':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        key = from_str(obj.get("key"))
        note = from_str(obj.get("note"))
        organization_id = UUID(obj.get("organizationId"))
        value = from_str(obj.get("value"))
        project_ids = from_union([from_none, lambda x: from_list(lambda x: UUID(x), x)], obj.get("projectIds"))
        return SecretPutRequest(id, key, note, organization_id, value, project_ids)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        result["key"] = from_str(self.key)
        result["note"] = from_str(self.note)
        result["organizationId"] = str(self.organization_id)
        result["value"] = from_str(self.value)
        if self.project_ids is not None:
            result["projectIds"] = from_union([from_none, lambda x: from_list(lambda x: str(x), x)], self.project_ids)
        return result


@dataclass
class SecretsCommand:
    """> Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Retrieve a secret by the provided identifier
    
    Returns: [SecretResponse](bitwarden::secrets_manager::secrets::SecretResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Retrieve secrets by the provided identifiers
    
    Returns: [SecretsResponse](bitwarden::secrets_manager::secrets::SecretsResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Creates a new secret in the provided organization using the given data
    
    Returns: [SecretResponse](bitwarden::secrets_manager::secrets::SecretResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Lists all secret identifiers of the given organization, to then retrieve each
    secret, use `CreateSecret`
    
    Returns:
    [SecretIdentifiersResponse](bitwarden::secrets_manager::secrets::SecretIdentifiersResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Updates an existing secret with the provided ID using the given data
    
    Returns: [SecretResponse](bitwarden::secrets_manager::secrets::SecretResponse)
    
    > Requires Authentication > Requires using an Access Token for login or calling Sync at
    least once Deletes all the secrets whose IDs match the provided ones
    
    Returns:
    [SecretsDeleteResponse](bitwarden::secrets_manager::secrets::SecretsDeleteResponse)
    """
    get: Optional[SecretGetRequest] = None
    get_by_ids: Optional[SecretsGetRequest] = None
    create: Optional[SecretCreateRequest] = None
    list: Optional[SecretIdentifiersRequest] = None
    update: Optional[SecretPutRequest] = None
    delete: Optional[SecretsDeleteRequest] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SecretsCommand':
        assert isinstance(obj, dict)
        get = from_union([SecretGetRequest.from_dict, from_none], obj.get("get"))
        get_by_ids = from_union([SecretsGetRequest.from_dict, from_none], obj.get("getByIds"))
        create = from_union([SecretCreateRequest.from_dict, from_none], obj.get("create"))
        list = from_union([SecretIdentifiersRequest.from_dict, from_none], obj.get("list"))
        update = from_union([SecretPutRequest.from_dict, from_none], obj.get("update"))
        delete = from_union([SecretsDeleteRequest.from_dict, from_none], obj.get("delete"))
        return SecretsCommand(get, get_by_ids, create, list, update, delete)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.get is not None:
            result["get"] = from_union([lambda x: to_class(SecretGetRequest, x), from_none], self.get)
        if self.get_by_ids is not None:
            result["getByIds"] = from_union([lambda x: to_class(SecretsGetRequest, x), from_none], self.get_by_ids)
        if self.create is not None:
            result["create"] = from_union([lambda x: to_class(SecretCreateRequest, x), from_none], self.create)
        if self.list is not None:
            result["list"] = from_union([lambda x: to_class(SecretIdentifiersRequest, x), from_none], self.list)
        if self.update is not None:
            result["update"] = from_union([lambda x: to_class(SecretPutRequest, x), from_none], self.update)
        if self.delete is not None:
            result["delete"] = from_union([lambda x: to_class(SecretsDeleteRequest, x), from_none], self.delete)
        return result


@dataclass
class SyncRequest:
    exclude_subdomains: Optional[bool] = None
    """Exclude the subdomains from the response, defaults to false"""

    @staticmethod
    def from_dict(obj: Any) -> 'SyncRequest':
        assert isinstance(obj, dict)
        exclude_subdomains = from_union([from_none, from_bool], obj.get("excludeSubdomains"))
        return SyncRequest(exclude_subdomains)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.exclude_subdomains is not None:
            result["excludeSubdomains"] = from_union([from_none, from_bool], self.exclude_subdomains)
        return result


@dataclass
class Command:
    """Login with username and password
    
    This command is for initiating an authentication handshake with Bitwarden. Authorization
    may fail due to requiring 2fa or captcha challenge completion despite accurate
    credentials.
    
    This command is not capable of handling authentication requiring 2fa or captcha.
    
    Returns: [PasswordLoginResponse](bitwarden::auth::login::PasswordLoginResponse)
    
    Login with API Key
    
    This command is for initiating an authentication handshake with Bitwarden.
    
    Returns: [ApiKeyLoginResponse](bitwarden::auth::login::ApiKeyLoginResponse)
    
    Login with Secrets Manager Access Token
    
    This command is for initiating an authentication handshake with Bitwarden.
    
    Returns: [ApiKeyLoginResponse](bitwarden::auth::login::ApiKeyLoginResponse)
    
    > Requires Authentication Get the API key of the currently authenticated user
    
    Returns: [UserApiKeyResponse](bitwarden::platform::UserApiKeyResponse)
    
    Get the user's passphrase
    
    Returns: String
    
    > Requires Authentication Retrieve all user data, ciphers and organizations the user is a
    part of
    
    Returns: [SyncResponse](bitwarden::platform::SyncResponse)
    """
    password_login: Optional[PasswordLoginRequest] = None
    api_key_login: Optional[APIKeyLoginRequest] = None
    access_token_login: Optional[AccessTokenLoginRequest] = None
    get_user_api_key: Optional[SecretVerificationRequest] = None
    fingerprint: Optional[FingerprintRequest] = None
    sync: Optional[SyncRequest] = None
    secrets: Optional[SecretsCommand] = None
    projects: Optional[ProjectsCommand] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Command':
        assert isinstance(obj, dict)
        password_login = from_union([PasswordLoginRequest.from_dict, from_none], obj.get("passwordLogin"))
        api_key_login = from_union([APIKeyLoginRequest.from_dict, from_none], obj.get("apiKeyLogin"))
        access_token_login = from_union([AccessTokenLoginRequest.from_dict, from_none], obj.get("accessTokenLogin"))
        get_user_api_key = from_union([SecretVerificationRequest.from_dict, from_none], obj.get("getUserApiKey"))
        fingerprint = from_union([FingerprintRequest.from_dict, from_none], obj.get("fingerprint"))
        sync = from_union([SyncRequest.from_dict, from_none], obj.get("sync"))
        secrets = from_union([SecretsCommand.from_dict, from_none], obj.get("secrets"))
        projects = from_union([ProjectsCommand.from_dict, from_none], obj.get("projects"))
        return Command(password_login, api_key_login, access_token_login, get_user_api_key, fingerprint, sync, secrets, projects)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.password_login is not None:
            result["passwordLogin"] = from_union([lambda x: to_class(PasswordLoginRequest, x), from_none], self.password_login)
        if self.api_key_login is not None:
            result["apiKeyLogin"] = from_union([lambda x: to_class(APIKeyLoginRequest, x), from_none], self.api_key_login)
        if self.access_token_login is not None:
            result["accessTokenLogin"] = from_union([lambda x: to_class(AccessTokenLoginRequest, x), from_none], self.access_token_login)
        if self.get_user_api_key is not None:
            result["getUserApiKey"] = from_union([lambda x: to_class(SecretVerificationRequest, x), from_none], self.get_user_api_key)
        if self.fingerprint is not None:
            result["fingerprint"] = from_union([lambda x: to_class(FingerprintRequest, x), from_none], self.fingerprint)
        if self.sync is not None:
            result["sync"] = from_union([lambda x: to_class(SyncRequest, x), from_none], self.sync)
        if self.secrets is not None:
            result["secrets"] = from_union([lambda x: to_class(SecretsCommand, x), from_none], self.secrets)
        if self.projects is not None:
            result["projects"] = from_union([lambda x: to_class(ProjectsCommand, x), from_none], self.projects)
        return result


@dataclass
class Authenticator:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'Authenticator':
        assert isinstance(obj, dict)
        return Authenticator()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class Duo:
    host: str
    signature: str

    @staticmethod
    def from_dict(obj: Any) -> 'Duo':
        assert isinstance(obj, dict)
        host = from_str(obj.get("host"))
        signature = from_str(obj.get("signature"))
        return Duo(host, signature)

    def to_dict(self) -> dict:
        result: dict = {}
        result["host"] = from_str(self.host)
        result["signature"] = from_str(self.signature)
        return result


@dataclass
class Email:
    email: str
    """The email to request a 2fa TOTP for"""

    @staticmethod
    def from_dict(obj: Any) -> 'Email':
        assert isinstance(obj, dict)
        email = from_str(obj.get("email"))
        return Email(email)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_str(self.email)
        return result


@dataclass
class Remember:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'Remember':
        assert isinstance(obj, dict)
        return Remember()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class WebAuthn:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'WebAuthn':
        assert isinstance(obj, dict)
        return WebAuthn()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class YubiKey:
    nfc: bool
    """Whether the stored yubikey supports near field communication"""

    @staticmethod
    def from_dict(obj: Any) -> 'YubiKey':
        assert isinstance(obj, dict)
        nfc = from_bool(obj.get("nfc"))
        return YubiKey(nfc)

    def to_dict(self) -> dict:
        result: dict = {}
        result["nfc"] = from_bool(self.nfc)
        return result


@dataclass
class TwoFactorProviders:
    authenticator: Optional[Authenticator] = None
    duo: Optional[Duo] = None
    """Duo-backed 2fa"""
    email: Optional[Email] = None
    """Email 2fa"""
    organization_duo: Optional[Duo] = None
    """Duo-backed 2fa operated by an organization the user is a member of"""
    remember: Optional[Remember] = None
    """Presence indicates the user has stored this device as bypassing 2fa"""
    web_authn: Optional[WebAuthn] = None
    """WebAuthn-backed 2fa"""
    yubi_key: Optional[YubiKey] = None
    """Yubikey-backed 2fa"""

    @staticmethod
    def from_dict(obj: Any) -> 'TwoFactorProviders':
        assert isinstance(obj, dict)
        authenticator = from_union([Authenticator.from_dict, from_none], obj.get("authenticator"))
        duo = from_union([Duo.from_dict, from_none], obj.get("duo"))
        email = from_union([Email.from_dict, from_none], obj.get("email"))
        organization_duo = from_union([Duo.from_dict, from_none], obj.get("organizationDuo"))
        remember = from_union([Remember.from_dict, from_none], obj.get("remember"))
        web_authn = from_union([WebAuthn.from_dict, from_none], obj.get("webAuthn"))
        yubi_key = from_union([YubiKey.from_dict, from_none], obj.get("yubiKey"))
        return TwoFactorProviders(authenticator, duo, email, organization_duo, remember, web_authn, yubi_key)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.authenticator is not None:
            result["authenticator"] = from_union([lambda x: to_class(Authenticator, x), from_none], self.authenticator)
        if self.duo is not None:
            result["duo"] = from_union([lambda x: to_class(Duo, x), from_none], self.duo)
        if self.email is not None:
            result["email"] = from_union([lambda x: to_class(Email, x), from_none], self.email)
        if self.organization_duo is not None:
            result["organizationDuo"] = from_union([lambda x: to_class(Duo, x), from_none], self.organization_duo)
        if self.remember is not None:
            result["remember"] = from_union([lambda x: to_class(Remember, x), from_none], self.remember)
        if self.web_authn is not None:
            result["webAuthn"] = from_union([lambda x: to_class(WebAuthn, x), from_none], self.web_authn)
        if self.yubi_key is not None:
            result["yubiKey"] = from_union([lambda x: to_class(YubiKey, x), from_none], self.yubi_key)
        return result


@dataclass
class APIKeyLoginResponse:
    authenticated: bool
    force_password_reset: bool
    """Whether or not the user is required to update their master password"""
    reset_master_password: bool
    """TODO: What does this do?"""
    two_factor: Optional[TwoFactorProviders] = None

    @staticmethod
    def from_dict(obj: Any) -> 'APIKeyLoginResponse':
        assert isinstance(obj, dict)
        authenticated = from_bool(obj.get("authenticated"))
        force_password_reset = from_bool(obj.get("forcePasswordReset"))
        reset_master_password = from_bool(obj.get("resetMasterPassword"))
        two_factor = from_union([TwoFactorProviders.from_dict, from_none], obj.get("twoFactor"))
        return APIKeyLoginResponse(authenticated, force_password_reset, reset_master_password, two_factor)

    def to_dict(self) -> dict:
        result: dict = {}
        result["authenticated"] = from_bool(self.authenticated)
        result["forcePasswordReset"] = from_bool(self.force_password_reset)
        result["resetMasterPassword"] = from_bool(self.reset_master_password)
        if self.two_factor is not None:
            result["twoFactor"] = from_union([lambda x: to_class(TwoFactorProviders, x), from_none], self.two_factor)
        return result


@dataclass
class ResponseForAPIKeyLoginResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[APIKeyLoginResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForAPIKeyLoginResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([APIKeyLoginResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForAPIKeyLoginResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(APIKeyLoginResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class CAPTCHAResponse:
    site_key: str
    """hcaptcha site key"""

    @staticmethod
    def from_dict(obj: Any) -> 'CAPTCHAResponse':
        assert isinstance(obj, dict)
        site_key = from_str(obj.get("siteKey"))
        return CAPTCHAResponse(site_key)

    def to_dict(self) -> dict:
        result: dict = {}
        result["siteKey"] = from_str(self.site_key)
        return result


@dataclass
class PasswordLoginResponse:
    authenticated: bool
    force_password_reset: bool
    """Whether or not the user is required to update their master password"""
    reset_master_password: bool
    """TODO: What does this do?"""
    captcha: Optional[CAPTCHAResponse] = None
    """The information required to present the user with a captcha challenge. Only present when
    authentication fails due to requiring validation of a captcha challenge.
    """
    two_factor: Optional[TwoFactorProviders] = None
    """The available two factor authentication options. Present only when authentication fails
    due to requiring a second authentication factor.
    """

    @staticmethod
    def from_dict(obj: Any) -> 'PasswordLoginResponse':
        assert isinstance(obj, dict)
        authenticated = from_bool(obj.get("authenticated"))
        force_password_reset = from_bool(obj.get("forcePasswordReset"))
        reset_master_password = from_bool(obj.get("resetMasterPassword"))
        captcha = from_union([CAPTCHAResponse.from_dict, from_none], obj.get("captcha"))
        two_factor = from_union([TwoFactorProviders.from_dict, from_none], obj.get("twoFactor"))
        return PasswordLoginResponse(authenticated, force_password_reset, reset_master_password, captcha, two_factor)

    def to_dict(self) -> dict:
        result: dict = {}
        result["authenticated"] = from_bool(self.authenticated)
        result["forcePasswordReset"] = from_bool(self.force_password_reset)
        result["resetMasterPassword"] = from_bool(self.reset_master_password)
        if self.captcha is not None:
            result["captcha"] = from_union([lambda x: to_class(CAPTCHAResponse, x), from_none], self.captcha)
        if self.two_factor is not None:
            result["twoFactor"] = from_union([lambda x: to_class(TwoFactorProviders, x), from_none], self.two_factor)
        return result


@dataclass
class ResponseForPasswordLoginResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[PasswordLoginResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForPasswordLoginResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([PasswordLoginResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForPasswordLoginResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(PasswordLoginResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class AccessTokenLoginResponse:
    authenticated: bool
    force_password_reset: bool
    """Whether or not the user is required to update their master password"""
    reset_master_password: bool
    """TODO: What does this do?"""
    two_factor: Optional[TwoFactorProviders] = None

    @staticmethod
    def from_dict(obj: Any) -> 'AccessTokenLoginResponse':
        assert isinstance(obj, dict)
        authenticated = from_bool(obj.get("authenticated"))
        force_password_reset = from_bool(obj.get("forcePasswordReset"))
        reset_master_password = from_bool(obj.get("resetMasterPassword"))
        two_factor = from_union([TwoFactorProviders.from_dict, from_none], obj.get("twoFactor"))
        return AccessTokenLoginResponse(authenticated, force_password_reset, reset_master_password, two_factor)

    def to_dict(self) -> dict:
        result: dict = {}
        result["authenticated"] = from_bool(self.authenticated)
        result["forcePasswordReset"] = from_bool(self.force_password_reset)
        result["resetMasterPassword"] = from_bool(self.reset_master_password)
        if self.two_factor is not None:
            result["twoFactor"] = from_union([lambda x: to_class(TwoFactorProviders, x), from_none], self.two_factor)
        return result


@dataclass
class ResponseForAccessTokenLoginResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[AccessTokenLoginResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForAccessTokenLoginResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([AccessTokenLoginResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForAccessTokenLoginResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(AccessTokenLoginResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class SecretIdentifierResponse:
    id: UUID
    key: str
    organization_id: UUID

    @staticmethod
    def from_dict(obj: Any) -> 'SecretIdentifierResponse':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        key = from_str(obj.get("key"))
        organization_id = UUID(obj.get("organizationId"))
        return SecretIdentifierResponse(id, key, organization_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        result["key"] = from_str(self.key)
        result["organizationId"] = str(self.organization_id)
        return result


@dataclass
class SecretIdentifiersResponse:
    data: List[SecretIdentifierResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'SecretIdentifiersResponse':
        assert isinstance(obj, dict)
        data = from_list(SecretIdentifierResponse.from_dict, obj.get("data"))
        return SecretIdentifiersResponse(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(SecretIdentifierResponse, x), self.data)
        return result


@dataclass
class ResponseForSecretIdentifiersResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[SecretIdentifiersResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForSecretIdentifiersResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([SecretIdentifiersResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForSecretIdentifiersResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(SecretIdentifiersResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class SecretResponse:
    creation_date: datetime
    id: UUID
    key: str
    note: str
    organization_id: UUID
    revision_date: datetime
    value: str
    project_id: Optional[UUID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SecretResponse':
        assert isinstance(obj, dict)
        creation_date = from_datetime(obj.get("creationDate"))
        id = UUID(obj.get("id"))
        key = from_str(obj.get("key"))
        note = from_str(obj.get("note"))
        organization_id = UUID(obj.get("organizationId"))
        revision_date = from_datetime(obj.get("revisionDate"))
        value = from_str(obj.get("value"))
        project_id = from_union([from_none, lambda x: UUID(x)], obj.get("projectId"))
        return SecretResponse(creation_date, id, key, note, organization_id, revision_date, value, project_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["creationDate"] = self.creation_date.isoformat()
        result["id"] = str(self.id)
        result["key"] = from_str(self.key)
        result["note"] = from_str(self.note)
        result["organizationId"] = str(self.organization_id)
        result["revisionDate"] = self.revision_date.isoformat()
        result["value"] = from_str(self.value)
        if self.project_id is not None:
            result["projectId"] = from_union([from_none, lambda x: str(x)], self.project_id)
        return result


@dataclass
class ResponseForSecretResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[SecretResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForSecretResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([SecretResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForSecretResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(SecretResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class SecretsResponse:
    data: List[SecretResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'SecretsResponse':
        assert isinstance(obj, dict)
        data = from_list(SecretResponse.from_dict, obj.get("data"))
        return SecretsResponse(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(SecretResponse, x), self.data)
        return result


@dataclass
class ResponseForSecretsResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[SecretsResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForSecretsResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([SecretsResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForSecretsResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(SecretsResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class SecretDeleteResponse:
    id: UUID
    error: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SecretDeleteResponse':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        error = from_union([from_none, from_str], obj.get("error"))
        return SecretDeleteResponse(id, error)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        if self.error is not None:
            result["error"] = from_union([from_none, from_str], self.error)
        return result


@dataclass
class SecretsDeleteResponse:
    data: List[SecretDeleteResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'SecretsDeleteResponse':
        assert isinstance(obj, dict)
        data = from_list(SecretDeleteResponse.from_dict, obj.get("data"))
        return SecretsDeleteResponse(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(SecretDeleteResponse, x), self.data)
        return result


@dataclass
class ResponseForSecretsDeleteResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[SecretsDeleteResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForSecretsDeleteResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([SecretsDeleteResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForSecretsDeleteResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(SecretsDeleteResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class ProjectResponse:
    creation_date: datetime
    id: UUID
    name: str
    organization_id: UUID
    revision_date: datetime

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectResponse':
        assert isinstance(obj, dict)
        creation_date = from_datetime(obj.get("creationDate"))
        id = UUID(obj.get("id"))
        name = from_str(obj.get("name"))
        organization_id = UUID(obj.get("organizationId"))
        revision_date = from_datetime(obj.get("revisionDate"))
        return ProjectResponse(creation_date, id, name, organization_id, revision_date)

    def to_dict(self) -> dict:
        result: dict = {}
        result["creationDate"] = self.creation_date.isoformat()
        result["id"] = str(self.id)
        result["name"] = from_str(self.name)
        result["organizationId"] = str(self.organization_id)
        result["revisionDate"] = self.revision_date.isoformat()
        return result


@dataclass
class ResponseForProjectResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[ProjectResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForProjectResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([ProjectResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForProjectResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(ProjectResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class ProjectsResponse:
    data: List[ProjectResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectsResponse':
        assert isinstance(obj, dict)
        data = from_list(ProjectResponse.from_dict, obj.get("data"))
        return ProjectsResponse(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(ProjectResponse, x), self.data)
        return result


@dataclass
class ResponseForProjectsResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[ProjectsResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForProjectsResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([ProjectsResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForProjectsResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(ProjectsResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class ProjectDeleteResponse:
    id: UUID
    error: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectDeleteResponse':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        error = from_union([from_none, from_str], obj.get("error"))
        return ProjectDeleteResponse(id, error)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        if self.error is not None:
            result["error"] = from_union([from_none, from_str], self.error)
        return result


@dataclass
class ProjectsDeleteResponse:
    data: List[ProjectDeleteResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectsDeleteResponse':
        assert isinstance(obj, dict)
        data = from_list(ProjectDeleteResponse.from_dict, obj.get("data"))
        return ProjectsDeleteResponse(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_list(lambda x: to_class(ProjectDeleteResponse, x), self.data)
        return result


@dataclass
class ResponseForProjectsDeleteResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[ProjectsDeleteResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForProjectsDeleteResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([ProjectsDeleteResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForProjectsDeleteResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(ProjectsDeleteResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class FingerprintResponse:
    fingerprint: str

    @staticmethod
    def from_dict(obj: Any) -> 'FingerprintResponse':
        assert isinstance(obj, dict)
        fingerprint = from_str(obj.get("fingerprint"))
        return FingerprintResponse(fingerprint)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fingerprint"] = from_str(self.fingerprint)
        return result


@dataclass
class ResponseForFingerprintResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[FingerprintResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForFingerprintResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([FingerprintResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForFingerprintResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(FingerprintResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


@dataclass
class Attachment:
    file_name: Optional[str] = None
    id: Optional[str] = None
    key: Optional[str] = None
    size: Optional[str] = None
    size_name: Optional[str] = None
    """Readable size, ex: "4.2 KB" or "1.43 GB\""""
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Attachment':
        assert isinstance(obj, dict)
        file_name = from_union([from_none, from_str], obj.get("fileName"))
        id = from_union([from_none, from_str], obj.get("id"))
        key = from_union([from_none, from_str], obj.get("key"))
        size = from_union([from_none, from_str], obj.get("size"))
        size_name = from_union([from_none, from_str], obj.get("sizeName"))
        url = from_union([from_none, from_str], obj.get("url"))
        return Attachment(file_name, id, key, size, size_name, url)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.file_name is not None:
            result["fileName"] = from_union([from_none, from_str], self.file_name)
        if self.id is not None:
            result["id"] = from_union([from_none, from_str], self.id)
        if self.key is not None:
            result["key"] = from_union([from_none, from_str], self.key)
        if self.size is not None:
            result["size"] = from_union([from_none, from_str], self.size)
        if self.size_name is not None:
            result["sizeName"] = from_union([from_none, from_str], self.size_name)
        if self.url is not None:
            result["url"] = from_union([from_none, from_str], self.url)
        return result


@dataclass
class Card:
    brand: Optional[str] = None
    cardholder_name: Optional[str] = None
    code: Optional[str] = None
    exp_month: Optional[str] = None
    exp_year: Optional[str] = None
    number: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Card':
        assert isinstance(obj, dict)
        brand = from_union([from_none, from_str], obj.get("brand"))
        cardholder_name = from_union([from_none, from_str], obj.get("cardholderName"))
        code = from_union([from_none, from_str], obj.get("code"))
        exp_month = from_union([from_none, from_str], obj.get("expMonth"))
        exp_year = from_union([from_none, from_str], obj.get("expYear"))
        number = from_union([from_none, from_str], obj.get("number"))
        return Card(brand, cardholder_name, code, exp_month, exp_year, number)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.brand is not None:
            result["brand"] = from_union([from_none, from_str], self.brand)
        if self.cardholder_name is not None:
            result["cardholderName"] = from_union([from_none, from_str], self.cardholder_name)
        if self.code is not None:
            result["code"] = from_union([from_none, from_str], self.code)
        if self.exp_month is not None:
            result["expMonth"] = from_union([from_none, from_str], self.exp_month)
        if self.exp_year is not None:
            result["expYear"] = from_union([from_none, from_str], self.exp_year)
        if self.number is not None:
            result["number"] = from_union([from_none, from_str], self.number)
        return result


class LinkedIDType(Enum):
    ADDRESS1 = "Address1"
    ADDRESS2 = "Address2"
    ADDRESS3 = "Address3"
    BRAND = "Brand"
    CARDHOLDER_NAME = "CardholderName"
    CITY = "City"
    CODE = "Code"
    COMPANY = "Company"
    COUNTRY = "Country"
    EMAIL = "Email"
    EXP_MONTH = "ExpMonth"
    EXP_YEAR = "ExpYear"
    FIRST_NAME = "FirstName"
    FULL_NAME = "FullName"
    LAST_NAME = "LastName"
    LICENSE_NUMBER = "LicenseNumber"
    MIDDLE_NAME = "MiddleName"
    NUMBER = "Number"
    PASSPORT_NUMBER = "PassportNumber"
    PASSWORD = "Password"
    PHONE = "Phone"
    POSTAL_CODE = "PostalCode"
    SSN = "Ssn"
    STATE = "State"
    TITLE = "Title"
    USERNAME = "Username"


class FieldType(Enum):
    BOOLEAN = "Boolean"
    HIDDEN = "Hidden"
    LINKED = "Linked"
    TEXT = "Text"


@dataclass
class Field:
    type: FieldType
    linked_id: Optional[LinkedIDType] = None
    name: Optional[str] = None
    value: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Field':
        assert isinstance(obj, dict)
        type = FieldType(obj.get("type"))
        linked_id = from_union([from_none, LinkedIDType], obj.get("linkedId"))
        name = from_union([from_none, from_str], obj.get("name"))
        value = from_union([from_none, from_str], obj.get("value"))
        return Field(type, linked_id, name, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = to_enum(FieldType, self.type)
        if self.linked_id is not None:
            result["linkedId"] = from_union([from_none, lambda x: to_enum(LinkedIDType, x)], self.linked_id)
        if self.name is not None:
            result["name"] = from_union([from_none, from_str], self.name)
        if self.value is not None:
            result["value"] = from_union([from_none, from_str], self.value)
        return result


@dataclass
class Identity:
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    license_number: Optional[str] = None
    middle_name: Optional[str] = None
    passport_number: Optional[str] = None
    phone: Optional[str] = None
    postal_code: Optional[str] = None
    ssn: Optional[str] = None
    state: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Identity':
        assert isinstance(obj, dict)
        address1 = from_union([from_none, from_str], obj.get("address1"))
        address2 = from_union([from_none, from_str], obj.get("address2"))
        address3 = from_union([from_none, from_str], obj.get("address3"))
        city = from_union([from_none, from_str], obj.get("city"))
        company = from_union([from_none, from_str], obj.get("company"))
        country = from_union([from_none, from_str], obj.get("country"))
        email = from_union([from_none, from_str], obj.get("email"))
        first_name = from_union([from_none, from_str], obj.get("firstName"))
        last_name = from_union([from_none, from_str], obj.get("lastName"))
        license_number = from_union([from_none, from_str], obj.get("licenseNumber"))
        middle_name = from_union([from_none, from_str], obj.get("middleName"))
        passport_number = from_union([from_none, from_str], obj.get("passportNumber"))
        phone = from_union([from_none, from_str], obj.get("phone"))
        postal_code = from_union([from_none, from_str], obj.get("postalCode"))
        ssn = from_union([from_none, from_str], obj.get("ssn"))
        state = from_union([from_none, from_str], obj.get("state"))
        title = from_union([from_none, from_str], obj.get("title"))
        username = from_union([from_none, from_str], obj.get("username"))
        return Identity(address1, address2, address3, city, company, country, email, first_name, last_name, license_number, middle_name, passport_number, phone, postal_code, ssn, state, title, username)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.address1 is not None:
            result["address1"] = from_union([from_none, from_str], self.address1)
        if self.address2 is not None:
            result["address2"] = from_union([from_none, from_str], self.address2)
        if self.address3 is not None:
            result["address3"] = from_union([from_none, from_str], self.address3)
        if self.city is not None:
            result["city"] = from_union([from_none, from_str], self.city)
        if self.company is not None:
            result["company"] = from_union([from_none, from_str], self.company)
        if self.country is not None:
            result["country"] = from_union([from_none, from_str], self.country)
        if self.email is not None:
            result["email"] = from_union([from_none, from_str], self.email)
        if self.first_name is not None:
            result["firstName"] = from_union([from_none, from_str], self.first_name)
        if self.last_name is not None:
            result["lastName"] = from_union([from_none, from_str], self.last_name)
        if self.license_number is not None:
            result["licenseNumber"] = from_union([from_none, from_str], self.license_number)
        if self.middle_name is not None:
            result["middleName"] = from_union([from_none, from_str], self.middle_name)
        if self.passport_number is not None:
            result["passportNumber"] = from_union([from_none, from_str], self.passport_number)
        if self.phone is not None:
            result["phone"] = from_union([from_none, from_str], self.phone)
        if self.postal_code is not None:
            result["postalCode"] = from_union([from_none, from_str], self.postal_code)
        if self.ssn is not None:
            result["ssn"] = from_union([from_none, from_str], self.ssn)
        if self.state is not None:
            result["state"] = from_union([from_none, from_str], self.state)
        if self.title is not None:
            result["title"] = from_union([from_none, from_str], self.title)
        if self.username is not None:
            result["username"] = from_union([from_none, from_str], self.username)
        return result


@dataclass
class LocalData:
    last_launched: Optional[int] = None
    last_used_date: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LocalData':
        assert isinstance(obj, dict)
        last_launched = from_union([from_none, from_int], obj.get("lastLaunched"))
        last_used_date = from_union([from_none, from_int], obj.get("lastUsedDate"))
        return LocalData(last_launched, last_used_date)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.last_launched is not None:
            result["lastLaunched"] = from_union([from_none, from_int], self.last_launched)
        if self.last_used_date is not None:
            result["lastUsedDate"] = from_union([from_none, from_int], self.last_used_date)
        return result


class URIMatchType(Enum):
    DOMAIN = "domain"
    EXACT = "exact"
    HOST = "host"
    NEVER = "never"
    REGULAR_EXPRESSION = "regularExpression"
    STARTS_WITH = "startsWith"


@dataclass
class LoginURI:
    match: Optional[URIMatchType] = None
    uri: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'LoginURI':
        assert isinstance(obj, dict)
        match = from_union([from_none, URIMatchType], obj.get("match"))
        uri = from_union([from_none, from_str], obj.get("uri"))
        return LoginURI(match, uri)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.match is not None:
            result["match"] = from_union([from_none, lambda x: to_enum(URIMatchType, x)], self.match)
        if self.uri is not None:
            result["uri"] = from_union([from_none, from_str], self.uri)
        return result


@dataclass
class Login:
    autofill_on_page_load: Optional[bool] = None
    password: Optional[str] = None
    password_revision_date: Optional[datetime] = None
    totp: Optional[str] = None
    uris: Optional[List[LoginURI]] = None
    username: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Login':
        assert isinstance(obj, dict)
        autofill_on_page_load = from_union([from_none, from_bool], obj.get("autofillOnPageLoad"))
        password = from_union([from_none, from_str], obj.get("password"))
        password_revision_date = from_union([from_none, from_datetime], obj.get("passwordRevisionDate"))
        totp = from_union([from_none, from_str], obj.get("totp"))
        uris = from_union([from_none, lambda x: from_list(LoginURI.from_dict, x)], obj.get("uris"))
        username = from_union([from_none, from_str], obj.get("username"))
        return Login(autofill_on_page_load, password, password_revision_date, totp, uris, username)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.autofill_on_page_load is not None:
            result["autofillOnPageLoad"] = from_union([from_none, from_bool], self.autofill_on_page_load)
        if self.password is not None:
            result["password"] = from_union([from_none, from_str], self.password)
        if self.password_revision_date is not None:
            result["passwordRevisionDate"] = from_union([from_none, lambda x: x.isoformat()], self.password_revision_date)
        if self.totp is not None:
            result["totp"] = from_union([from_none, from_str], self.totp)
        if self.uris is not None:
            result["uris"] = from_union([from_none, lambda x: from_list(lambda x: to_class(LoginURI, x), x)], self.uris)
        if self.username is not None:
            result["username"] = from_union([from_none, from_str], self.username)
        return result


@dataclass
class PasswordHistory:
    last_used_date: datetime
    password: str

    @staticmethod
    def from_dict(obj: Any) -> 'PasswordHistory':
        assert isinstance(obj, dict)
        last_used_date = from_datetime(obj.get("lastUsedDate"))
        password = from_str(obj.get("password"))
        return PasswordHistory(last_used_date, password)

    def to_dict(self) -> dict:
        result: dict = {}
        result["lastUsedDate"] = self.last_used_date.isoformat()
        result["password"] = from_str(self.password)
        return result


class CipherRepromptType(Enum):
    NONE = "None"
    PASSWORD = "Password"


class SecureNoteType(Enum):
    GENERIC = "Generic"


@dataclass
class SecureNote:
    type: SecureNoteType

    @staticmethod
    def from_dict(obj: Any) -> 'SecureNote':
        assert isinstance(obj, dict)
        type = SecureNoteType(obj.get("type"))
        return SecureNote(type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = to_enum(SecureNoteType, self.type)
        return result


class CipherType(Enum):
    CARD = "Card"
    IDENTITY = "Identity"
    LOGIN = "Login"
    SECURE_NOTE = "SecureNote"


@dataclass
class Cipher:
    collection_ids: List[UUID]
    creation_date: datetime
    edit: bool
    favorite: bool
    name: str
    organization_use_totp: bool
    reprompt: CipherRepromptType
    revision_date: datetime
    type: CipherType
    view_password: bool
    attachments: Optional[List[Attachment]] = None
    card: Optional[Card] = None
    deleted_date: Optional[datetime] = None
    fields: Optional[List[Field]] = None
    folder_id: Optional[UUID] = None
    id: Optional[UUID] = None
    identity: Optional[Identity] = None
    key: Optional[str] = None
    """More recent ciphers uses individual encryption keys to encrypt the other fields of the
    Cipher.
    """
    local_data: Optional[LocalData] = None
    login: Optional[Login] = None
    notes: Optional[str] = None
    organization_id: Optional[UUID] = None
    password_history: Optional[List[PasswordHistory]] = None
    secure_note: Optional[SecureNote] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Cipher':
        assert isinstance(obj, dict)
        collection_ids = from_list(lambda x: UUID(x), obj.get("collectionIds"))
        creation_date = from_datetime(obj.get("creationDate"))
        edit = from_bool(obj.get("edit"))
        favorite = from_bool(obj.get("favorite"))
        name = from_str(obj.get("name"))
        organization_use_totp = from_bool(obj.get("organizationUseTotp"))
        reprompt = CipherRepromptType(obj.get("reprompt"))
        revision_date = from_datetime(obj.get("revisionDate"))
        type = CipherType(obj.get("type"))
        view_password = from_bool(obj.get("viewPassword"))
        attachments = from_union([from_none, lambda x: from_list(Attachment.from_dict, x)], obj.get("attachments"))
        card = from_union([Card.from_dict, from_none], obj.get("card"))
        deleted_date = from_union([from_none, from_datetime], obj.get("deletedDate"))
        fields = from_union([from_none, lambda x: from_list(Field.from_dict, x)], obj.get("fields"))
        folder_id = from_union([from_none, lambda x: UUID(x)], obj.get("folderId"))
        id = from_union([from_none, lambda x: UUID(x)], obj.get("id"))
        identity = from_union([Identity.from_dict, from_none], obj.get("identity"))
        key = from_union([from_none, from_str], obj.get("key"))
        local_data = from_union([LocalData.from_dict, from_none], obj.get("localData"))
        login = from_union([Login.from_dict, from_none], obj.get("login"))
        notes = from_union([from_none, from_str], obj.get("notes"))
        organization_id = from_union([from_none, lambda x: UUID(x)], obj.get("organizationId"))
        password_history = from_union([from_none, lambda x: from_list(PasswordHistory.from_dict, x)], obj.get("passwordHistory"))
        secure_note = from_union([SecureNote.from_dict, from_none], obj.get("secureNote"))
        return Cipher(collection_ids, creation_date, edit, favorite, name, organization_use_totp, reprompt, revision_date, type, view_password, attachments, card, deleted_date, fields, folder_id, id, identity, key, local_data, login, notes, organization_id, password_history, secure_note)

    def to_dict(self) -> dict:
        result: dict = {}
        result["collectionIds"] = from_list(lambda x: str(x), self.collection_ids)
        result["creationDate"] = self.creation_date.isoformat()
        result["edit"] = from_bool(self.edit)
        result["favorite"] = from_bool(self.favorite)
        result["name"] = from_str(self.name)
        result["organizationUseTotp"] = from_bool(self.organization_use_totp)
        result["reprompt"] = to_enum(CipherRepromptType, self.reprompt)
        result["revisionDate"] = self.revision_date.isoformat()
        result["type"] = to_enum(CipherType, self.type)
        result["viewPassword"] = from_bool(self.view_password)
        if self.attachments is not None:
            result["attachments"] = from_union([from_none, lambda x: from_list(lambda x: to_class(Attachment, x), x)], self.attachments)
        if self.card is not None:
            result["card"] = from_union([lambda x: to_class(Card, x), from_none], self.card)
        if self.deleted_date is not None:
            result["deletedDate"] = from_union([from_none, lambda x: x.isoformat()], self.deleted_date)
        if self.fields is not None:
            result["fields"] = from_union([from_none, lambda x: from_list(lambda x: to_class(Field, x), x)], self.fields)
        if self.folder_id is not None:
            result["folderId"] = from_union([from_none, lambda x: str(x)], self.folder_id)
        if self.id is not None:
            result["id"] = from_union([from_none, lambda x: str(x)], self.id)
        if self.identity is not None:
            result["identity"] = from_union([lambda x: to_class(Identity, x), from_none], self.identity)
        if self.key is not None:
            result["key"] = from_union([from_none, from_str], self.key)
        if self.local_data is not None:
            result["localData"] = from_union([lambda x: to_class(LocalData, x), from_none], self.local_data)
        if self.login is not None:
            result["login"] = from_union([lambda x: to_class(Login, x), from_none], self.login)
        if self.notes is not None:
            result["notes"] = from_union([from_none, from_str], self.notes)
        if self.organization_id is not None:
            result["organizationId"] = from_union([from_none, lambda x: str(x)], self.organization_id)
        if self.password_history is not None:
            result["passwordHistory"] = from_union([from_none, lambda x: from_list(lambda x: to_class(PasswordHistory, x), x)], self.password_history)
        if self.secure_note is not None:
            result["secureNote"] = from_union([lambda x: to_class(SecureNote, x), from_none], self.secure_note)
        return result


@dataclass
class Collection:
    hide_passwords: bool
    name: str
    organization_id: UUID
    read_only: bool
    external_id: Optional[str] = None
    id: Optional[UUID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Collection':
        assert isinstance(obj, dict)
        hide_passwords = from_bool(obj.get("hidePasswords"))
        name = from_str(obj.get("name"))
        organization_id = UUID(obj.get("organizationId"))
        read_only = from_bool(obj.get("readOnly"))
        external_id = from_union([from_none, from_str], obj.get("externalId"))
        id = from_union([from_none, lambda x: UUID(x)], obj.get("id"))
        return Collection(hide_passwords, name, organization_id, read_only, external_id, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["hidePasswords"] = from_bool(self.hide_passwords)
        result["name"] = from_str(self.name)
        result["organizationId"] = str(self.organization_id)
        result["readOnly"] = from_bool(self.read_only)
        if self.external_id is not None:
            result["externalId"] = from_union([from_none, from_str], self.external_id)
        if self.id is not None:
            result["id"] = from_union([from_none, lambda x: str(x)], self.id)
        return result


@dataclass
class GlobalDomains:
    domains: List[str]
    excluded: bool
    type: int

    @staticmethod
    def from_dict(obj: Any) -> 'GlobalDomains':
        assert isinstance(obj, dict)
        domains = from_list(from_str, obj.get("domains"))
        excluded = from_bool(obj.get("excluded"))
        type = from_int(obj.get("type"))
        return GlobalDomains(domains, excluded, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["domains"] = from_list(from_str, self.domains)
        result["excluded"] = from_bool(self.excluded)
        result["type"] = from_int(self.type)
        return result


@dataclass
class DomainResponse:
    equivalent_domains: List[List[str]]
    global_equivalent_domains: List[GlobalDomains]

    @staticmethod
    def from_dict(obj: Any) -> 'DomainResponse':
        assert isinstance(obj, dict)
        equivalent_domains = from_list(lambda x: from_list(from_str, x), obj.get("equivalentDomains"))
        global_equivalent_domains = from_list(GlobalDomains.from_dict, obj.get("globalEquivalentDomains"))
        return DomainResponse(equivalent_domains, global_equivalent_domains)

    def to_dict(self) -> dict:
        result: dict = {}
        result["equivalentDomains"] = from_list(lambda x: from_list(from_str, x), self.equivalent_domains)
        result["globalEquivalentDomains"] = from_list(lambda x: to_class(GlobalDomains, x), self.global_equivalent_domains)
        return result


@dataclass
class Folder:
    name: str
    revision_date: datetime
    id: Optional[UUID] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Folder':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        revision_date = from_datetime(obj.get("revisionDate"))
        id = from_union([from_none, lambda x: UUID(x)], obj.get("id"))
        return Folder(name, revision_date, id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["revisionDate"] = self.revision_date.isoformat()
        if self.id is not None:
            result["id"] = from_union([from_none, lambda x: str(x)], self.id)
        return result


class PolicyType(Enum):
    ACTIVATE_AUTOFILL = "ActivateAutofill"
    DISABLE_PERSONAL_VAULT_EXPORT = "DisablePersonalVaultExport"
    DISABLE_SEND = "DisableSend"
    MASTER_PASSWORD = "MasterPassword"
    MAXIMUM_VAULT_TIMEOUT = "MaximumVaultTimeout"
    PASSWORD_GENERATOR = "PasswordGenerator"
    PERSONAL_OWNERSHIP = "PersonalOwnership"
    REQUIRE_SSO = "RequireSso"
    RESET_PASSWORD = "ResetPassword"
    SEND_OPTIONS = "SendOptions"
    SINGLE_ORG = "SingleOrg"
    TWO_FACTOR_AUTHENTICATION = "TwoFactorAuthentication"


@dataclass
class Policy:
    enabled: bool
    id: UUID
    organization_id: UUID
    type: PolicyType
    data: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Policy':
        assert isinstance(obj, dict)
        enabled = from_bool(obj.get("enabled"))
        id = UUID(obj.get("id"))
        organization_id = UUID(obj.get("organization_id"))
        type = PolicyType(obj.get("type"))
        data = from_union([from_none, lambda x: from_dict(lambda x: x, x)], obj.get("data"))
        return Policy(enabled, id, organization_id, type, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["enabled"] = from_bool(self.enabled)
        result["id"] = str(self.id)
        result["organization_id"] = str(self.organization_id)
        result["type"] = to_enum(PolicyType, self.type)
        if self.data is not None:
            result["data"] = from_union([from_none, lambda x: from_dict(lambda x: x, x)], self.data)
        return result


@dataclass
class ProfileOrganizationResponse:
    id: UUID

    @staticmethod
    def from_dict(obj: Any) -> 'ProfileOrganizationResponse':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        return ProfileOrganizationResponse(id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        return result


@dataclass
class ProfileResponse:
    """Data about the user, including their encryption keys and the organizations they are a
    part of
    """
    email: str
    id: UUID
    name: str
    organizations: List[ProfileOrganizationResponse]

    @staticmethod
    def from_dict(obj: Any) -> 'ProfileResponse':
        assert isinstance(obj, dict)
        email = from_str(obj.get("email"))
        id = UUID(obj.get("id"))
        name = from_str(obj.get("name"))
        organizations = from_list(ProfileOrganizationResponse.from_dict, obj.get("organizations"))
        return ProfileResponse(email, id, name, organizations)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_str(self.email)
        result["id"] = str(self.id)
        result["name"] = from_str(self.name)
        result["organizations"] = from_list(lambda x: to_class(ProfileOrganizationResponse, x), self.organizations)
        return result


@dataclass
class SendFile:
    file_name: str
    id: Optional[str] = None
    size: Optional[str] = None
    size_name: Optional[str] = None
    """Readable size, ex: "4.2 KB" or "1.43 GB\""""

    @staticmethod
    def from_dict(obj: Any) -> 'SendFile':
        assert isinstance(obj, dict)
        file_name = from_str(obj.get("fileName"))
        id = from_union([from_none, from_str], obj.get("id"))
        size = from_union([from_none, from_str], obj.get("size"))
        size_name = from_union([from_none, from_str], obj.get("sizeName"))
        return SendFile(file_name, id, size, size_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fileName"] = from_str(self.file_name)
        if self.id is not None:
            result["id"] = from_union([from_none, from_str], self.id)
        if self.size is not None:
            result["size"] = from_union([from_none, from_str], self.size)
        if self.size_name is not None:
            result["sizeName"] = from_union([from_none, from_str], self.size_name)
        return result


@dataclass
class SendText:
    hidden: bool
    text: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SendText':
        assert isinstance(obj, dict)
        hidden = from_bool(obj.get("hidden"))
        text = from_union([from_none, from_str], obj.get("text"))
        return SendText(hidden, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["hidden"] = from_bool(self.hidden)
        if self.text is not None:
            result["text"] = from_union([from_none, from_str], self.text)
        return result


class SendType(Enum):
    FILE = "File"
    TEXT = "Text"


@dataclass
class Send:
    access_count: int
    deletion_date: datetime
    disabled: bool
    hide_email: bool
    key: str
    name: str
    revision_date: datetime
    type: SendType
    access_id: Optional[str] = None
    expiration_date: Optional[datetime] = None
    file: Optional[SendFile] = None
    id: Optional[UUID] = None
    max_access_count: Optional[int] = None
    notes: Optional[str] = None
    password: Optional[str] = None
    text: Optional[SendText] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Send':
        assert isinstance(obj, dict)
        access_count = from_int(obj.get("accessCount"))
        deletion_date = from_datetime(obj.get("deletionDate"))
        disabled = from_bool(obj.get("disabled"))
        hide_email = from_bool(obj.get("hideEmail"))
        key = from_str(obj.get("key"))
        name = from_str(obj.get("name"))
        revision_date = from_datetime(obj.get("revisionDate"))
        type = SendType(obj.get("type"))
        access_id = from_union([from_none, from_str], obj.get("accessId"))
        expiration_date = from_union([from_none, from_datetime], obj.get("expirationDate"))
        file = from_union([SendFile.from_dict, from_none], obj.get("file"))
        id = from_union([from_none, lambda x: UUID(x)], obj.get("id"))
        max_access_count = from_union([from_none, from_int], obj.get("maxAccessCount"))
        notes = from_union([from_none, from_str], obj.get("notes"))
        password = from_union([from_none, from_str], obj.get("password"))
        text = from_union([SendText.from_dict, from_none], obj.get("text"))
        return Send(access_count, deletion_date, disabled, hide_email, key, name, revision_date, type, access_id, expiration_date, file, id, max_access_count, notes, password, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["accessCount"] = from_int(self.access_count)
        result["deletionDate"] = self.deletion_date.isoformat()
        result["disabled"] = from_bool(self.disabled)
        result["hideEmail"] = from_bool(self.hide_email)
        result["key"] = from_str(self.key)
        result["name"] = from_str(self.name)
        result["revisionDate"] = self.revision_date.isoformat()
        result["type"] = to_enum(SendType, self.type)
        if self.access_id is not None:
            result["accessId"] = from_union([from_none, from_str], self.access_id)
        if self.expiration_date is not None:
            result["expirationDate"] = from_union([from_none, lambda x: x.isoformat()], self.expiration_date)
        if self.file is not None:
            result["file"] = from_union([lambda x: to_class(SendFile, x), from_none], self.file)
        if self.id is not None:
            result["id"] = from_union([from_none, lambda x: str(x)], self.id)
        if self.max_access_count is not None:
            result["maxAccessCount"] = from_union([from_none, from_int], self.max_access_count)
        if self.notes is not None:
            result["notes"] = from_union([from_none, from_str], self.notes)
        if self.password is not None:
            result["password"] = from_union([from_none, from_str], self.password)
        if self.text is not None:
            result["text"] = from_union([lambda x: to_class(SendText, x), from_none], self.text)
        return result


@dataclass
class SyncResponse:
    ciphers: List[Cipher]
    """List of ciphers accessible by the user"""
    collections: List[Collection]
    folders: List[Folder]
    policies: List[Policy]
    profile: ProfileResponse
    """Data about the user, including their encryption keys and the organizations they are a
    part of
    """
    sends: List[Send]
    domains: Optional[DomainResponse] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SyncResponse':
        assert isinstance(obj, dict)
        ciphers = from_list(Cipher.from_dict, obj.get("ciphers"))
        collections = from_list(Collection.from_dict, obj.get("collections"))
        folders = from_list(Folder.from_dict, obj.get("folders"))
        policies = from_list(Policy.from_dict, obj.get("policies"))
        profile = ProfileResponse.from_dict(obj.get("profile"))
        sends = from_list(Send.from_dict, obj.get("sends"))
        domains = from_union([DomainResponse.from_dict, from_none], obj.get("domains"))
        return SyncResponse(ciphers, collections, folders, policies, profile, sends, domains)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ciphers"] = from_list(lambda x: to_class(Cipher, x), self.ciphers)
        result["collections"] = from_list(lambda x: to_class(Collection, x), self.collections)
        result["folders"] = from_list(lambda x: to_class(Folder, x), self.folders)
        result["policies"] = from_list(lambda x: to_class(Policy, x), self.policies)
        result["profile"] = to_class(ProfileResponse, self.profile)
        result["sends"] = from_list(lambda x: to_class(Send, x), self.sends)
        if self.domains is not None:
            result["domains"] = from_union([lambda x: to_class(DomainResponse, x), from_none], self.domains)
        return result


@dataclass
class ResponseForSyncResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[SyncResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForSyncResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([SyncResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForSyncResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(SyncResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


class LoginLinkedIDType(Enum):
    PASSWORD = "Password"
    USERNAME = "Username"


class CardLinkedIDType(Enum):
    BRAND = "Brand"
    CARDHOLDER_NAME = "CardholderName"
    CODE = "Code"
    EXP_MONTH = "ExpMonth"
    EXP_YEAR = "ExpYear"
    NUMBER = "Number"


class IdentityLinkedIDType(Enum):
    ADDRESS1 = "Address1"
    ADDRESS2 = "Address2"
    ADDRESS3 = "Address3"
    CITY = "City"
    COMPANY = "Company"
    COUNTRY = "Country"
    EMAIL = "Email"
    FIRST_NAME = "FirstName"
    FULL_NAME = "FullName"
    LAST_NAME = "LastName"
    LICENSE_NUMBER = "LicenseNumber"
    MIDDLE_NAME = "MiddleName"
    PASSPORT_NUMBER = "PassportNumber"
    PHONE = "Phone"
    POSTAL_CODE = "PostalCode"
    SSN = "Ssn"
    STATE = "State"
    TITLE = "Title"
    USERNAME = "Username"


@dataclass
class UserAPIKeyResponse:
    api_key: str
    """The user's API key, which represents the client_secret portion of an oauth request."""

    @staticmethod
    def from_dict(obj: Any) -> 'UserAPIKeyResponse':
        assert isinstance(obj, dict)
        api_key = from_str(obj.get("apiKey"))
        return UserAPIKeyResponse(api_key)

    def to_dict(self) -> dict:
        result: dict = {}
        result["apiKey"] = from_str(self.api_key)
        return result


@dataclass
class ResponseForUserAPIKeyResponse:
    success: bool
    """Whether or not the SDK request succeeded."""
    data: Optional[UserAPIKeyResponse] = None
    """The response data. Populated if `success` is true."""
    error_message: Optional[str] = None
    """A message for any error that may occur. Populated if `success` is false."""

    @staticmethod
    def from_dict(obj: Any) -> 'ResponseForUserAPIKeyResponse':
        assert isinstance(obj, dict)
        success = from_bool(obj.get("success"))
        data = from_union([UserAPIKeyResponse.from_dict, from_none], obj.get("data"))
        error_message = from_union([from_none, from_str], obj.get("errorMessage"))
        return ResponseForUserAPIKeyResponse(success, data, error_message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["success"] = from_bool(self.success)
        if self.data is not None:
            result["data"] = from_union([lambda x: to_class(UserAPIKeyResponse, x), from_none], self.data)
        if self.error_message is not None:
            result["errorMessage"] = from_union([from_none, from_str], self.error_message)
        return result


def client_settings_from_dict(s: Any) -> ClientSettings:
    return ClientSettings.from_dict(s)


def client_settings_to_dict(x: ClientSettings) -> Any:
    return to_class(ClientSettings, x)


def device_type_from_dict(s: Any) -> DeviceType:
    return DeviceType(s)


def device_type_to_dict(x: DeviceType) -> Any:
    return to_enum(DeviceType, x)


def command_from_dict(s: Any) -> Command:
    return Command.from_dict(s)


def command_to_dict(x: Command) -> Any:
    return to_class(Command, x)


def password_login_request_from_dict(s: Any) -> PasswordLoginRequest:
    return PasswordLoginRequest.from_dict(s)


def password_login_request_to_dict(x: PasswordLoginRequest) -> Any:
    return to_class(PasswordLoginRequest, x)


def two_factor_request_from_dict(s: Any) -> TwoFactorRequest:
    return TwoFactorRequest.from_dict(s)


def two_factor_request_to_dict(x: TwoFactorRequest) -> Any:
    return to_class(TwoFactorRequest, x)


def two_factor_provider_from_dict(s: Any) -> TwoFactorProvider:
    return TwoFactorProvider(s)


def two_factor_provider_to_dict(x: TwoFactorProvider) -> Any:
    return to_enum(TwoFactorProvider, x)


def kdf_from_dict(s: Any) -> Kdf:
    return Kdf.from_dict(s)


def kdf_to_dict(x: Kdf) -> Any:
    return to_class(Kdf, x)


def api_key_login_request_from_dict(s: Any) -> APIKeyLoginRequest:
    return APIKeyLoginRequest.from_dict(s)


def api_key_login_request_to_dict(x: APIKeyLoginRequest) -> Any:
    return to_class(APIKeyLoginRequest, x)


def access_token_login_request_from_dict(s: Any) -> AccessTokenLoginRequest:
    return AccessTokenLoginRequest.from_dict(s)


def access_token_login_request_to_dict(x: AccessTokenLoginRequest) -> Any:
    return to_class(AccessTokenLoginRequest, x)


def secret_verification_request_from_dict(s: Any) -> SecretVerificationRequest:
    return SecretVerificationRequest.from_dict(s)


def secret_verification_request_to_dict(x: SecretVerificationRequest) -> Any:
    return to_class(SecretVerificationRequest, x)


def fingerprint_request_from_dict(s: Any) -> FingerprintRequest:
    return FingerprintRequest.from_dict(s)


def fingerprint_request_to_dict(x: FingerprintRequest) -> Any:
    return to_class(FingerprintRequest, x)


def sync_request_from_dict(s: Any) -> SyncRequest:
    return SyncRequest.from_dict(s)


def sync_request_to_dict(x: SyncRequest) -> Any:
    return to_class(SyncRequest, x)


def secrets_command_from_dict(s: Any) -> SecretsCommand:
    return SecretsCommand.from_dict(s)


def secrets_command_to_dict(x: SecretsCommand) -> Any:
    return to_class(SecretsCommand, x)


def secret_get_request_from_dict(s: Any) -> SecretGetRequest:
    return SecretGetRequest.from_dict(s)


def secret_get_request_to_dict(x: SecretGetRequest) -> Any:
    return to_class(SecretGetRequest, x)


def secrets_get_request_from_dict(s: Any) -> SecretsGetRequest:
    return SecretsGetRequest.from_dict(s)


def secrets_get_request_to_dict(x: SecretsGetRequest) -> Any:
    return to_class(SecretsGetRequest, x)


def secret_create_request_from_dict(s: Any) -> SecretCreateRequest:
    return SecretCreateRequest.from_dict(s)


def secret_create_request_to_dict(x: SecretCreateRequest) -> Any:
    return to_class(SecretCreateRequest, x)


def secret_identifiers_request_from_dict(s: Any) -> SecretIdentifiersRequest:
    return SecretIdentifiersRequest.from_dict(s)


def secret_identifiers_request_to_dict(x: SecretIdentifiersRequest) -> Any:
    return to_class(SecretIdentifiersRequest, x)


def secret_put_request_from_dict(s: Any) -> SecretPutRequest:
    return SecretPutRequest.from_dict(s)


def secret_put_request_to_dict(x: SecretPutRequest) -> Any:
    return to_class(SecretPutRequest, x)


def secrets_delete_request_from_dict(s: Any) -> SecretsDeleteRequest:
    return SecretsDeleteRequest.from_dict(s)


def secrets_delete_request_to_dict(x: SecretsDeleteRequest) -> Any:
    return to_class(SecretsDeleteRequest, x)


def projects_command_from_dict(s: Any) -> ProjectsCommand:
    return ProjectsCommand.from_dict(s)


def projects_command_to_dict(x: ProjectsCommand) -> Any:
    return to_class(ProjectsCommand, x)


def project_get_request_from_dict(s: Any) -> ProjectGetRequest:
    return ProjectGetRequest.from_dict(s)


def project_get_request_to_dict(x: ProjectGetRequest) -> Any:
    return to_class(ProjectGetRequest, x)


def project_create_request_from_dict(s: Any) -> ProjectCreateRequest:
    return ProjectCreateRequest.from_dict(s)


def project_create_request_to_dict(x: ProjectCreateRequest) -> Any:
    return to_class(ProjectCreateRequest, x)


def projects_list_request_from_dict(s: Any) -> ProjectsListRequest:
    return ProjectsListRequest.from_dict(s)


def projects_list_request_to_dict(x: ProjectsListRequest) -> Any:
    return to_class(ProjectsListRequest, x)


def project_put_request_from_dict(s: Any) -> ProjectPutRequest:
    return ProjectPutRequest.from_dict(s)


def project_put_request_to_dict(x: ProjectPutRequest) -> Any:
    return to_class(ProjectPutRequest, x)


def projects_delete_request_from_dict(s: Any) -> ProjectsDeleteRequest:
    return ProjectsDeleteRequest.from_dict(s)


def projects_delete_request_to_dict(x: ProjectsDeleteRequest) -> Any:
    return to_class(ProjectsDeleteRequest, x)


def response_for_api_key_login_response_from_dict(s: Any) -> ResponseForAPIKeyLoginResponse:
    return ResponseForAPIKeyLoginResponse.from_dict(s)


def response_for_api_key_login_response_to_dict(x: ResponseForAPIKeyLoginResponse) -> Any:
    return to_class(ResponseForAPIKeyLoginResponse, x)


def api_key_login_response_from_dict(s: Any) -> APIKeyLoginResponse:
    return APIKeyLoginResponse.from_dict(s)


def api_key_login_response_to_dict(x: APIKeyLoginResponse) -> Any:
    return to_class(APIKeyLoginResponse, x)


def two_factor_providers_from_dict(s: Any) -> TwoFactorProviders:
    return TwoFactorProviders.from_dict(s)


def two_factor_providers_to_dict(x: TwoFactorProviders) -> Any:
    return to_class(TwoFactorProviders, x)


def authenticator_from_dict(s: Any) -> Authenticator:
    return Authenticator.from_dict(s)


def authenticator_to_dict(x: Authenticator) -> Any:
    return to_class(Authenticator, x)


def email_from_dict(s: Any) -> Email:
    return Email.from_dict(s)


def email_to_dict(x: Email) -> Any:
    return to_class(Email, x)


def duo_from_dict(s: Any) -> Duo:
    return Duo.from_dict(s)


def duo_to_dict(x: Duo) -> Any:
    return to_class(Duo, x)


def yubi_key_from_dict(s: Any) -> YubiKey:
    return YubiKey.from_dict(s)


def yubi_key_to_dict(x: YubiKey) -> Any:
    return to_class(YubiKey, x)


def remember_from_dict(s: Any) -> Remember:
    return Remember.from_dict(s)


def remember_to_dict(x: Remember) -> Any:
    return to_class(Remember, x)


def web_authn_from_dict(s: Any) -> WebAuthn:
    return WebAuthn.from_dict(s)


def web_authn_to_dict(x: WebAuthn) -> Any:
    return to_class(WebAuthn, x)


def response_for_password_login_response_from_dict(s: Any) -> ResponseForPasswordLoginResponse:
    return ResponseForPasswordLoginResponse.from_dict(s)


def response_for_password_login_response_to_dict(x: ResponseForPasswordLoginResponse) -> Any:
    return to_class(ResponseForPasswordLoginResponse, x)


def password_login_response_from_dict(s: Any) -> PasswordLoginResponse:
    return PasswordLoginResponse.from_dict(s)


def password_login_response_to_dict(x: PasswordLoginResponse) -> Any:
    return to_class(PasswordLoginResponse, x)


def captcha_response_from_dict(s: Any) -> CAPTCHAResponse:
    return CAPTCHAResponse.from_dict(s)


def captcha_response_to_dict(x: CAPTCHAResponse) -> Any:
    return to_class(CAPTCHAResponse, x)


def response_for_access_token_login_response_from_dict(s: Any) -> ResponseForAccessTokenLoginResponse:
    return ResponseForAccessTokenLoginResponse.from_dict(s)


def response_for_access_token_login_response_to_dict(x: ResponseForAccessTokenLoginResponse) -> Any:
    return to_class(ResponseForAccessTokenLoginResponse, x)


def access_token_login_response_from_dict(s: Any) -> AccessTokenLoginResponse:
    return AccessTokenLoginResponse.from_dict(s)


def access_token_login_response_to_dict(x: AccessTokenLoginResponse) -> Any:
    return to_class(AccessTokenLoginResponse, x)


def response_for_secret_identifiers_response_from_dict(s: Any) -> ResponseForSecretIdentifiersResponse:
    return ResponseForSecretIdentifiersResponse.from_dict(s)


def response_for_secret_identifiers_response_to_dict(x: ResponseForSecretIdentifiersResponse) -> Any:
    return to_class(ResponseForSecretIdentifiersResponse, x)


def secret_identifiers_response_from_dict(s: Any) -> SecretIdentifiersResponse:
    return SecretIdentifiersResponse.from_dict(s)


def secret_identifiers_response_to_dict(x: SecretIdentifiersResponse) -> Any:
    return to_class(SecretIdentifiersResponse, x)


def secret_identifier_response_from_dict(s: Any) -> SecretIdentifierResponse:
    return SecretIdentifierResponse.from_dict(s)


def secret_identifier_response_to_dict(x: SecretIdentifierResponse) -> Any:
    return to_class(SecretIdentifierResponse, x)


def response_for_secret_response_from_dict(s: Any) -> ResponseForSecretResponse:
    return ResponseForSecretResponse.from_dict(s)


def response_for_secret_response_to_dict(x: ResponseForSecretResponse) -> Any:
    return to_class(ResponseForSecretResponse, x)


def secret_response_from_dict(s: Any) -> SecretResponse:
    return SecretResponse.from_dict(s)


def secret_response_to_dict(x: SecretResponse) -> Any:
    return to_class(SecretResponse, x)


def response_for_secrets_response_from_dict(s: Any) -> ResponseForSecretsResponse:
    return ResponseForSecretsResponse.from_dict(s)


def response_for_secrets_response_to_dict(x: ResponseForSecretsResponse) -> Any:
    return to_class(ResponseForSecretsResponse, x)


def secrets_response_from_dict(s: Any) -> SecretsResponse:
    return SecretsResponse.from_dict(s)


def secrets_response_to_dict(x: SecretsResponse) -> Any:
    return to_class(SecretsResponse, x)


def response_for_secrets_delete_response_from_dict(s: Any) -> ResponseForSecretsDeleteResponse:
    return ResponseForSecretsDeleteResponse.from_dict(s)


def response_for_secrets_delete_response_to_dict(x: ResponseForSecretsDeleteResponse) -> Any:
    return to_class(ResponseForSecretsDeleteResponse, x)


def secrets_delete_response_from_dict(s: Any) -> SecretsDeleteResponse:
    return SecretsDeleteResponse.from_dict(s)


def secrets_delete_response_to_dict(x: SecretsDeleteResponse) -> Any:
    return to_class(SecretsDeleteResponse, x)


def secret_delete_response_from_dict(s: Any) -> SecretDeleteResponse:
    return SecretDeleteResponse.from_dict(s)


def secret_delete_response_to_dict(x: SecretDeleteResponse) -> Any:
    return to_class(SecretDeleteResponse, x)


def response_for_project_response_from_dict(s: Any) -> ResponseForProjectResponse:
    return ResponseForProjectResponse.from_dict(s)


def response_for_project_response_to_dict(x: ResponseForProjectResponse) -> Any:
    return to_class(ResponseForProjectResponse, x)


def project_response_from_dict(s: Any) -> ProjectResponse:
    return ProjectResponse.from_dict(s)


def project_response_to_dict(x: ProjectResponse) -> Any:
    return to_class(ProjectResponse, x)


def response_for_projects_response_from_dict(s: Any) -> ResponseForProjectsResponse:
    return ResponseForProjectsResponse.from_dict(s)


def response_for_projects_response_to_dict(x: ResponseForProjectsResponse) -> Any:
    return to_class(ResponseForProjectsResponse, x)


def projects_response_from_dict(s: Any) -> ProjectsResponse:
    return ProjectsResponse.from_dict(s)


def projects_response_to_dict(x: ProjectsResponse) -> Any:
    return to_class(ProjectsResponse, x)


def response_for_projects_delete_response_from_dict(s: Any) -> ResponseForProjectsDeleteResponse:
    return ResponseForProjectsDeleteResponse.from_dict(s)


def response_for_projects_delete_response_to_dict(x: ResponseForProjectsDeleteResponse) -> Any:
    return to_class(ResponseForProjectsDeleteResponse, x)


def projects_delete_response_from_dict(s: Any) -> ProjectsDeleteResponse:
    return ProjectsDeleteResponse.from_dict(s)


def projects_delete_response_to_dict(x: ProjectsDeleteResponse) -> Any:
    return to_class(ProjectsDeleteResponse, x)


def project_delete_response_from_dict(s: Any) -> ProjectDeleteResponse:
    return ProjectDeleteResponse.from_dict(s)


def project_delete_response_to_dict(x: ProjectDeleteResponse) -> Any:
    return to_class(ProjectDeleteResponse, x)


def response_for_fingerprint_response_from_dict(s: Any) -> ResponseForFingerprintResponse:
    return ResponseForFingerprintResponse.from_dict(s)


def response_for_fingerprint_response_to_dict(x: ResponseForFingerprintResponse) -> Any:
    return to_class(ResponseForFingerprintResponse, x)


def fingerprint_response_from_dict(s: Any) -> FingerprintResponse:
    return FingerprintResponse.from_dict(s)


def fingerprint_response_to_dict(x: FingerprintResponse) -> Any:
    return to_class(FingerprintResponse, x)


def response_for_sync_response_from_dict(s: Any) -> ResponseForSyncResponse:
    return ResponseForSyncResponse.from_dict(s)


def response_for_sync_response_to_dict(x: ResponseForSyncResponse) -> Any:
    return to_class(ResponseForSyncResponse, x)


def sync_response_from_dict(s: Any) -> SyncResponse:
    return SyncResponse.from_dict(s)


def sync_response_to_dict(x: SyncResponse) -> Any:
    return to_class(SyncResponse, x)


def profile_response_from_dict(s: Any) -> ProfileResponse:
    return ProfileResponse.from_dict(s)


def profile_response_to_dict(x: ProfileResponse) -> Any:
    return to_class(ProfileResponse, x)


def profile_organization_response_from_dict(s: Any) -> ProfileOrganizationResponse:
    return ProfileOrganizationResponse.from_dict(s)


def profile_organization_response_to_dict(x: ProfileOrganizationResponse) -> Any:
    return to_class(ProfileOrganizationResponse, x)


def folder_from_dict(s: Any) -> Folder:
    return Folder.from_dict(s)


def folder_to_dict(x: Folder) -> Any:
    return to_class(Folder, x)


def enc_string_from_dict(s: Any) -> str:
    return from_str(s)


def enc_string_to_dict(x: str) -> Any:
    return from_str(x)


def collection_from_dict(s: Any) -> Collection:
    return Collection.from_dict(s)


def collection_to_dict(x: Collection) -> Any:
    return to_class(Collection, x)


def cipher_from_dict(s: Any) -> Cipher:
    return Cipher.from_dict(s)


def cipher_to_dict(x: Cipher) -> Any:
    return to_class(Cipher, x)


def cipher_type_from_dict(s: Any) -> CipherType:
    return CipherType(s)


def cipher_type_to_dict(x: CipherType) -> Any:
    return to_enum(CipherType, x)


def login_from_dict(s: Any) -> Login:
    return Login.from_dict(s)


def login_to_dict(x: Login) -> Any:
    return to_class(Login, x)


def login_uri_from_dict(s: Any) -> LoginURI:
    return LoginURI.from_dict(s)


def login_uri_to_dict(x: LoginURI) -> Any:
    return to_class(LoginURI, x)


def uri_match_type_from_dict(s: Any) -> URIMatchType:
    return URIMatchType(s)


def uri_match_type_to_dict(x: URIMatchType) -> Any:
    return to_enum(URIMatchType, x)


def identity_from_dict(s: Any) -> Identity:
    return Identity.from_dict(s)


def identity_to_dict(x: Identity) -> Any:
    return to_class(Identity, x)


def card_from_dict(s: Any) -> Card:
    return Card.from_dict(s)


def card_to_dict(x: Card) -> Any:
    return to_class(Card, x)


def secure_note_from_dict(s: Any) -> SecureNote:
    return SecureNote.from_dict(s)


def secure_note_to_dict(x: SecureNote) -> Any:
    return to_class(SecureNote, x)


def secure_note_type_from_dict(s: Any) -> SecureNoteType:
    return SecureNoteType(s)


def secure_note_type_to_dict(x: SecureNoteType) -> Any:
    return to_enum(SecureNoteType, x)


def cipher_reprompt_type_from_dict(s: Any) -> CipherRepromptType:
    return CipherRepromptType(s)


def cipher_reprompt_type_to_dict(x: CipherRepromptType) -> Any:
    return to_enum(CipherRepromptType, x)


def local_data_from_dict(s: Any) -> LocalData:
    return LocalData.from_dict(s)


def local_data_to_dict(x: LocalData) -> Any:
    return to_class(LocalData, x)


def attachment_from_dict(s: Any) -> Attachment:
    return Attachment.from_dict(s)


def attachment_to_dict(x: Attachment) -> Any:
    return to_class(Attachment, x)


def field_from_dict(s: Any) -> Field:
    return Field.from_dict(s)


def field_to_dict(x: Field) -> Any:
    return to_class(Field, x)


def field_type_from_dict(s: Any) -> FieldType:
    return FieldType(s)


def field_type_to_dict(x: FieldType) -> Any:
    return to_enum(FieldType, x)


def linked_id_type_from_dict(s: Any) -> LinkedIDType:
    return LinkedIDType(s)


def linked_id_type_to_dict(x: LinkedIDType) -> Any:
    return to_enum(LinkedIDType, x)


def login_linked_id_type_from_dict(s: Any) -> LoginLinkedIDType:
    return LoginLinkedIDType(s)


def login_linked_id_type_to_dict(x: LoginLinkedIDType) -> Any:
    return to_enum(LoginLinkedIDType, x)


def card_linked_id_type_from_dict(s: Any) -> CardLinkedIDType:
    return CardLinkedIDType(s)


def card_linked_id_type_to_dict(x: CardLinkedIDType) -> Any:
    return to_enum(CardLinkedIDType, x)


def identity_linked_id_type_from_dict(s: Any) -> IdentityLinkedIDType:
    return IdentityLinkedIDType(s)


def identity_linked_id_type_to_dict(x: IdentityLinkedIDType) -> Any:
    return to_enum(IdentityLinkedIDType, x)


def password_history_from_dict(s: Any) -> PasswordHistory:
    return PasswordHistory.from_dict(s)


def password_history_to_dict(x: PasswordHistory) -> Any:
    return to_class(PasswordHistory, x)


def domain_response_from_dict(s: Any) -> DomainResponse:
    return DomainResponse.from_dict(s)


def domain_response_to_dict(x: DomainResponse) -> Any:
    return to_class(DomainResponse, x)


def global_domains_from_dict(s: Any) -> GlobalDomains:
    return GlobalDomains.from_dict(s)


def global_domains_to_dict(x: GlobalDomains) -> Any:
    return to_class(GlobalDomains, x)


def policy_from_dict(s: Any) -> Policy:
    return Policy.from_dict(s)


def policy_to_dict(x: Policy) -> Any:
    return to_class(Policy, x)


def policy_type_from_dict(s: Any) -> PolicyType:
    return PolicyType(s)


def policy_type_to_dict(x: PolicyType) -> Any:
    return to_enum(PolicyType, x)


def send_from_dict(s: Any) -> Send:
    return Send.from_dict(s)


def send_to_dict(x: Send) -> Any:
    return to_class(Send, x)


def send_type_from_dict(s: Any) -> SendType:
    return SendType(s)


def send_type_to_dict(x: SendType) -> Any:
    return to_enum(SendType, x)


def send_file_from_dict(s: Any) -> SendFile:
    return SendFile.from_dict(s)


def send_file_to_dict(x: SendFile) -> Any:
    return to_class(SendFile, x)


def send_text_from_dict(s: Any) -> SendText:
    return SendText.from_dict(s)


def send_text_to_dict(x: SendText) -> Any:
    return to_class(SendText, x)


def response_for_user_api_key_response_from_dict(s: Any) -> ResponseForUserAPIKeyResponse:
    return ResponseForUserAPIKeyResponse.from_dict(s)


def response_for_user_api_key_response_to_dict(x: ResponseForUserAPIKeyResponse) -> Any:
    return to_class(ResponseForUserAPIKeyResponse, x)


def user_api_key_response_from_dict(s: Any) -> UserAPIKeyResponse:
    return UserAPIKeyResponse.from_dict(s)


def user_api_key_response_to_dict(x: UserAPIKeyResponse) -> Any:
    return to_class(UserAPIKeyResponse, x)

