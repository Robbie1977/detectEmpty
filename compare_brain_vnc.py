#!/usr/bin/env python3
"""
Compare Brain and VNC folder pairs to identify Brain folders with no expression
(VNC has data but Brain doesn't, or Brain wlz is significantly smaller than VNC wlz)
"""

# All known folder codes with their templates
folder_pairs = {
    '3ftr': ('Brain: 121.27 MB, wlz: 158KB', 'VNC: 121.82 MB, wlz: 2.3KB (EMPTY)'),
    '3ftt': ('Brain: 98.20 MB, wlz: 120KB', 'VNC: 718.13 MB, wlz: many files'),
    '3ftv': ('Brain: 157.03 MB, wlz: 211KB', 'VNC: 154.56 MB, wlz: varies'),
    '3ftq': ('Brain: 132.34 MB, wlz: 173KB', 'VNC: Unknown'),
    '3fts': ('Brain: 102.81 MB, wlz: 130KB', 'VNC: Unknown'),
}

print("Analyzing folder pairs with both Brain (VFB_00101567) and VNC (VFB_00200000) data:")
print("=" * 100)
print("\nKnown pairs where we have data for both templates:")
for folder, brain_info, vnc_info in folder_pairs.items():
    print(f"\n{folder}:")
    print(f"  {brain_info}")
    print(f"  {vnc_info}")

print("\n" + "=" * 100)
print("KEY INSIGHT from earlier analysis:")
print("=" * 100)
print("""
- 3ftr VNC: volume.wlz = 2.3 KB with completely empty thumbnail (NO SIGNAL)
- 3ftr Brain: volume.wlz = 158 KB with visible signal in thumbnail
- This means 3ftr has Brain data but NO VNC data!

The pattern should be: Look for Brain folders where wlz is very small (< 50KB?) 
BUT the corresponding VNC folder (same folder code) has larger wlz files.

Or: Brain folders that should be blocked are those with NO corresponding VNC expression.
""")

print("\nFolders from the original list that have BOTH Brain AND VNC versions:")
print("-" * 100)
both_versions = ['3ftr', '3ftt', '3ftv']
print(f"Folders with both: {both_versions}")

print("\nFolders from the original list that have ONLY Brain versions:")
print("-" * 100)
brain_only = ['3kle', '3kjs', '3kjn', '3k8z', '3kce', '3juw', '3k83', '3kcj', '3k4v',
              '3kaw', '3kek', '3k63', '3k64', '3jzn', '3kas', '3kcx', '3k9d', '3kbt',
              '3jy2', '3jx8', '3k1g', '3k3g', '3k3a', '3k5m', '3k5n', '3kfz', '3k94',
              '3k3b', '3k4b', '3jrf', '3juy', '3jx7', '3jrh', '3jrl', '3jut', '3jv5',
              '3kex', '3k8c', '3juu', '3jv4', '3js8', '3jyf', '3jzi', '3k9f', '3k9y',
              '3k9c', '3jw1', '3jv7', '3k0m', '3k04', '3kff', '3k8u', '3jv0', '3jxa',
              '3k40', '3k4c', '3k51', '3k4k', '3k4l', '3k7b', '3kfg', '3k7t', '3kfw',
              '3ke4', '3k6j', '3ker', '3k4e', '3js7', '3jt0', '3jzj', '3k4r', '3k0d',
              '3k8w', '3k9b', '3jwv', '3k5l', '3k74', '3kfs', '3kcs', '3kao', '3k1l',
              '3k0v', '3kf1', '3k7k', '3jrq', '3jtk', '3k39', '3k17', '3kat', '3k80',
              '3k9m', '3kam', '3ftq', '3fts']
print(f"Count: {len(brain_only)} folders\n")
print("NOTE: These Brain-only folders might be the ones to block if they're truly empty!")
