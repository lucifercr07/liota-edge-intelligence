x="dell5k"
x+=`cat /etc/hostname`
y=\"$x\"
echo $y
sed -i "s/^\(EdgeSystemName\s*=\s*\).*\$/\1$y/" sampleProp.conf
