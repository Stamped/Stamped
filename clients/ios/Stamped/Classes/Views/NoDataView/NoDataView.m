//
//  NoDataView.m
//  Fav.TV
//
//  Created by Devin Doty on 2/9/11.
//  Copyright 2011 enormego. All rights reserved.
//


#import "NoDataView.h"

@implementation NoDataView

@synthesize imageView=_imageView;
@synthesize textLabel=_textLabel;
@synthesize detailTextLabel=_detailedTextLabel;

- (id)initWithFrame:(CGRect)frame {

    if ((self = [super initWithFrame:frame])) {
		
        self.backgroundColor = [UIColor clearColor];
		CGFloat offset = 30;
	
		UIImageView *view = [[UIImageView alloc] initWithFrame:CGRectMake(offset, floor((self.bounds.size.height/2) - ((200.0f/2)+offset)), floorf(self.bounds.size.width-(offset*2)), 200.0f)];
        view.backgroundColor = [UIColor whiteColor];
		view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
		[self addSubview:view];
		self.imageView = view;
		[view release];
		
		UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(offset, CGRectGetMaxY(_imageView.frame), floorf(self.bounds.size.width - (offset*2)), 20.0f)];
		label.lineBreakMode	= UILineBreakModeTailTruncation;
		label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
		label.font = [UIFont boldSystemFontOfSize:17];
		label.numberOfLines = 1;
		label.backgroundColor = self.backgroundColor;
		label.textColor = [UIColor colorWithRed:0.180f green:0.180f blue:0.180f alpha:1.0f];
		label.textAlignment = UITextAlignmentCenter;
		label.shadowOffset = CGSizeMake(0.0f, 1.0f);
		label.shadowColor = [UIColor whiteColor];
		[self addSubview:label];
		self.textLabel = label;
		[label release];
		
		label = [[UILabel alloc] initWithFrame:CGRectMake(offset, CGRectGetMaxY(_textLabel.frame), floorf(self.bounds.size.width - (offset*2)), 20.0f)];
		label.lineBreakMode = UILineBreakModeWordWrap;
		label.numberOfLines = 6;
		label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
		label.font = [UIFont systemFontOfSize:14];
		label.backgroundColor = self.backgroundColor;
		label.textColor = [UIColor colorWithRed:0.403f green:0.403f blue:0.403f alpha:1.0f];
		label.textAlignment = UITextAlignmentCenter;
		label.shadowOffset = CGSizeMake(0.0f, 1.0f);
		label.shadowColor = [UIColor whiteColor];
		[self addSubview:label];
		self.detailTextLabel = label;
		[label release];
		
	}
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGFloat offset = 34;
    
    if (self.imageView.image) {
        CGSize size = self.imageView.image.size;
        self.imageView.frame = CGRectMake(floorf((self.bounds.size.width/2)-(size.width/2)), floor((self.bounds.size.height/2) - ((size.height/2)+offset)), size.width, size.height);
    } else {
        self.imageView.frame = CGRectMake(0, 0, self.bounds.size.width, 20);
    }
    
    
    self.textLabel.frame = CGRectMake(offset, CGRectGetMaxY(_imageView.frame)+14, floorf(self.bounds.size.width - (offset*2)), 20.0f);
    
    CGSize size = [self.detailTextLabel.text sizeWithFont:self.detailTextLabel.font constrainedToSize:CGSizeMake(floorf(self.bounds.size.width - (offset*2)), CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
    self.detailTextLabel.frame = CGRectMake(offset, CGRectGetMaxY(_textLabel.frame), floorf(self.bounds.size.width - (offset*2)), size.height);
    
    if (_detailedTextLayer!=nil) {
        _detailedTextLayer.frame = self.detailTextLabel.frame;
    }
    
}


#pragma mark - Setters

- (void)setBackgroundColor:(UIColor *)color{
	[super setBackgroundColor:color];
	
	_imageView.backgroundColor = color;
	_textLabel.backgroundColor = color;
	_detailedTextLabel.backgroundColor = color;
	
}

- (void)setTitle:(NSString *)title detailedTitle:(id)detailTitle imageName:(NSString*)imageName {
	
	self.textLabel.text = title;
    if ([detailTitle isKindOfClass:[NSMutableAttributedString class]]) {
        self.detailTextLabel.text = [detailTitle string];
	} else {
        self.detailTextLabel.text = detailTitle;
    }
    
	if (detailTitle) {
		CGSize size = [self.detailTextLabel.text sizeWithFont:self.detailTextLabel.font constrainedToSize:CGSizeMake(self.bounds.size.width-40.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
		self.detailTextLabel.frame = CGRectMake(20.0f, CGRectGetMaxY(_textLabel.frame) + 4, self.bounds.size.width-40.0f, size.height);
	}
	
    if ((NSNull*)imageName != [NSNull null]) {
        if (imageName) {
            
            UIImage *_image = [UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:([[UIScreen mainScreen] scale] == 2.0) ? [imageName stringByAppendingString:@"@2x"] : imageName ofType:@"png"]];
            
            if (_image) {
                self.imageView.image = _image;
            }
            
        } else {
            /*
            NSString *fileName = @"no_data_default";
            if ([[UIScreen mainScreen] scale] == 2) {
                fileName = [fileName stringByAppendingString:@"@2x"];
            }
            self.imageView.image = [UIImage imageWithContentsOfFile:[[NSBundle mainBundle] pathForResource:fileName ofType:@"png"]];
            */
        }
    }
	
    if ([detailTitle isKindOfClass:[NSAttributedString class]]) {
    
        self.detailTextLabel.hidden = YES;
        
        CATextLayer *layer = [CATextLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.frame = self.detailTextLabel.frame;
        layer.backgroundColor = self.backgroundColor.CGColor;
        layer.wrapped = YES;
        layer.alignmentMode = @"center";
        layer.string = detailTitle;
        [self.layer addSublayer:layer];
        _detailedTextLayer = layer;
        
    }
    
    [self setNeedsLayout];

}


#pragma mark - Dealloc

- (void)dealloc {
	self.detailTextLabel=nil;
	self.textLabel=nil;
	self.imageView=nil;
    [super dealloc];
}


@end
