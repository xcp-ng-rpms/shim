%global package_speccommit 4c135ce7d899d71d4727a0fdb845d75bc00c25f5
%global usver 16.1
%global xsver 4
%global xsrel %{xsver}%{?xscount}%{?xshash}

# debug info empty, disable it to avoid RPM build errors
%global debug_package %{nil}

%define tarball_version 16.1

Summary: First-stage UEFI bootloader
Name: shim
Version: 16.1
Release: %{?xsrel}~secureboot.1%{?dist}
License: BSD
Source0: shim-16.1.tar.bz2
Source1: BOOTX64.CSV
Patch0: ignore-mm-missing.patch
Patch1: 0001-pe-Fix-PF-in-GRUB-after-memattrs-call.patch

BuildRequires: xcpsign-macros-test
BuildRequires: sbsigntools
Requires: certwrapper
Conflicts: grub <= 2.12-5

%description
Initial UEFI bootloader that handles chaining to a trusted full bootloader
under secure boot environments. This package contains the dev-signed
version.

%package unsigned
Summary: Unsigned first-stage UEFI bootloader

%description unsigned
Initial UEFI bootloader that handles chaining to a trusted full bootloader
under secure boot environments. This package contains the unsigned version.

%package mokmanager
Summary: Mok Manager

%description mokmanager
Contains the mmx64.efi executable for enrolling Machine Owner Keys.
This package contains the dev-signed version.

%prep
%autosetup -p1

%build
%fetchcert -c SHIM_EMBEDDED_SIGN_KEY_XCP9 -o pub.cer
grep -q shim.xs data/sbat.csv ||
    echo 'shim.xs,1,Cloud Software Group,shim,%{version}-%{release},mailto:security@xenserver.com' >> data/sbat.csv
make POST_PROCESS_PE_FLAGS=-n VENDOR_CERT_FILE=pub.cer IGNORE_MM_MISSING=1

%sign -c SHIM_SIGN_KEY_XCP9 -i shimx64.efi -o shimx64-signed.efi
%sign -c SHIM_EMBEDDED_SIGN_KEY_XCP9 -i fbx64.efi -o fbx64-signed.efi
%sign -c SHIM_EMBEDDED_SIGN_KEY_XCP9 -i mmx64.efi -o mmx64-signed.efi

%check
%fetchcert -c SHIM_SIGN_KEY_XCP9 -o shim_sign_key.cer
pesigcheck -c shim_sign_key.cer -n 0 -i shimx64-signed.efi

%install
mkdir -p %{buildroot}/boot/efi/EFI/xenserver
cp shimx64.efi %{buildroot}/boot/efi/EFI/xenserver/shimx64-unsigned.efi
cp shimx64-signed.efi %{buildroot}/boot/efi/EFI/xenserver/shimx64.efi
cp mmx64-signed.efi %{buildroot}/boot/efi/EFI/xenserver/mmx64.efi
install -m 644 %{SOURCE1} %{buildroot}/boot/efi/EFI/xenserver

mkdir -p %{buildroot}/boot/efi/EFI/BOOT
cp shimx64-signed.efi %{buildroot}/boot/efi/EFI/BOOT/BOOTX64.EFI
cp fbx64-signed.efi %{buildroot}/boot/efi/EFI/BOOT/fbx64.efi

%files
/boot/efi/EFI/BOOT
/boot/efi/EFI/xenserver/BOOTX64.CSV
/boot/efi/EFI/xenserver/shimx64.efi

%files unsigned
/boot/efi/EFI/xenserver/shimx64-unsigned.efi

%files mokmanager
/boot/efi/EFI/xenserver/mmx64.efi

%changelog
* Wed Jun 10 2026 Corentin Oparowski <corentin.oparowski@vates.tech> - 16.1-5
- change certs and deps to test with xcp-ng

* Thu Oct 09 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.1-4
- Fix key usage in %check

* Wed Oct 08 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.1-3
- CP-47917: Re-sign with new key

* Tue Sep 16 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.1-2
- CP-309737: Support fallback boot via BOOTX64.EFI
- CA-417210: Add vendor-specific line to SBAT

* Mon Aug 18 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.1-1
- Update to Shim 16.1
- CP-308091: Fix PF in GRUB after memattrs call

* Wed Aug 06 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-7
- Update to Shim 16.1-rc1
- CA-414790: Fix a crash when Xen exits early

* Tue Jul 15 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-6
- CA-413422: shim: Optionally tolerate MokManager being missing
- CP-54174: Avoid using *FLAGS from RPM

* Fri Jul 04 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-5
- Rebuild

* Wed Jun 25 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-4
- CP-308443: Use latest automatic revocations

* Wed May 21 2025 Frediano Ziglio <frediano.ziglio@cloud.com> - 16.0-3
- CP-308117: Rebuild due to signature issue

* Thu Apr 17 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-2
- CP-49469: Depend on python3-xssign

* Wed Mar 26 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0-1
- CP-53944: Update to 16.0

* Fri Mar 14 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 16.0~rc1-1
- CP-53944: Update to 16.0-rc1

* Tue Mar 05 2024 Ross Lagerwall <ross.lagerwall@citrix.com> - 15.8-1
- Update to 15.8

* Thu Feb 02 2023 Ross Lagerwall <ross.lagerwall@citrix.com> - 15.7-1
- Initial packaging
