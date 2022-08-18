#!/bin/sh

if [ $# -eq 1 ] ; then
    VERSION=$1
else
    echo "Script must be called with a single argument containing a new version string"
    exit 1
fi

TODAY=$(date -I)

echo "Updating version in QGIS Plugin at ./buildings/metadata.txt to $VERSION"
sed -i "s/^version=.*/version=$VERSION/g" ./buildings/metadata.txt

echo "Adding todays date $TODAY to changelog at ./CHANGELOG.rst"
sed -i "/Unreleased/{n;n;s/.*/$TODAY\n/}" ./CHANGELOG.rst

# Replace Unreleased header with version number in CHANGELOG
echo "Replacing 'Unreleased' section header with '$VERSION' in changelog at ./CHANGELOG.rst"
sed -i "s/Unreleased/$VERSION/g" ./CHANGELOG.rst
