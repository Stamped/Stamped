//
//  NoDataView.m
//
//  Created by Devin Doty on 2/9/11.
//  Copyright 2011. All rights reserved.
//


#import "NoDataView.h"

@implementation NoDataView

@synthesize imageView=_imageView;

- (id)initWithFrame:(CGRect)frame {

    if ((self = [super initWithFrame:frame])) {
		
        self.backgroundColor = [UIColor whiteColor];
	
        UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"no_data_hud.png"]];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        CGRect frame = view.frame;
        frame.origin.x = (self.bounds.size.width - frame.size.width)/2;
        frame.origin.y = (self.bounds.size.height - frame.size.height)/2;
        view.frame = frame;
        view.backgroundColor = [UIColor whiteColor];
		view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
		[self addSubview:view];
		self.imageView = view;
		[view release];
		
	}
    return self;
}

- (void)dealloc {
	self.imageView=nil;
    [super dealloc];
}


@end
