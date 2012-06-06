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


#pragma mark - Setters

- (void)setupWithTitle:(NSString*)title detailTitle:(NSString*)detailTitle {
    
    [self.imageView.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.lineBreakMode	= UILineBreakModeTailTruncation;
    label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
    label.font = [UIFont boldSystemFontOfSize:17];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f];
    label.shadowOffset = CGSizeMake(0.0f, -1.0f);
    label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
    [self.imageView addSubview:label];
    [label release];
    
    label.text = title;
    [label sizeToFit];
    
    CGRect frame = label.frame;
    frame.origin.x = floorf((self.imageView.bounds.size.width-frame.size.width)/2);
    frame.origin.y = 36.0f;
    label.frame = frame;
    CGFloat maxY = CGRectGetMaxY(label.frame);

    label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.lineBreakMode = UILineBreakModeWordWrap;
    label.numberOfLines = 3;
    label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
    label.font = [UIFont boldSystemFontOfSize:13];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
    label.textAlignment = UITextAlignmentCenter;
    label.shadowOffset = CGSizeMake(0.0f, -1.0f);
    label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
    [self.imageView addSubview:label];
    [label release];
    
    label.text = detailTitle;
    
    CGSize size = [label.text sizeWithFont:label.font constrainedToSize:CGSizeMake(240.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
    frame = label.frame;
    frame.size = size;
    frame.origin.x = floorf((self.imageView.bounds.size.width-size.width)/2);
    frame.origin.y = floorf(maxY + 4.0f);;
    label.frame = frame;

}


@end
