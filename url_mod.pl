#! /usr/bin/perl -w

@list = `grep -lr '\"\/' . | grep \.html\$`;
#@list = `grep -lr '\"\/' . | grep \.js\$`;

foreach my $file (@list) {
	chomp($file);
	print("========= $file =========\n");
	
	@urls = `grep '\"\/' $file`;
	foreach my $url (@urls) {
		print("---$url");
	}
}