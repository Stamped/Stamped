//
//  STConfirmationView.m
//  Stamped
//
//  Created by Landon Judkins on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConfirmationView.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

@interface STConfirmationView ()

- (void)dismissed:(id)button;

@property (nonatomic, readwrite, retain) UIImageView* imageView;

@end

@implementation STConfirmationView

@synthesize imageView = _imageView;

- (id)initWithTille:(NSString*)title subtitle:(NSString*)subtitle andIconImage:(UIImage*)image {
    CGFloat height = 58;
    CGFloat width = 294;
    self = [super initWithFrame:CGRectMake(0, 0, width, height)];
    if (self) {
        self.backgroundColor = [UIColor colorWithRed:.35 green:.35 blue:.35 alpha:1];
        self.layer.cornerRadius = 4.0;
        self.layer.borderColor =[UIColor colorWithRed:.25 green:.25 blue:.25 alpha:1].CGColor;
        self.layer.borderWidth = 2.0;
        self.layer.shadowColor = [UIColor blackColor].CGColor;
        self.layer.shadowOpacity = .6;
        self.layer.shadowRadius = 5.0;
        self.layer.shadowOffset = CGSizeMake(0, 4);
        
        UIView* buttom = [Util tapViewWithFrame:CGRectMake(0, 0, width, height) target:self selector:@selector(dismissed:) andMessage:nil];
        [self addSubview:buttom];
        
        _imageView = [[UIImageView alloc]  initWithFrame:CGRectMake(12, 12, 32, 32)];
        _imageView.image = image;
        [self addSubview:_imageView];
        
        CGFloat titleOffsetY = 20;
        
        if (subtitle != nil) {
            titleOffsetY = 10;
        }
        
        UIView* titleView = [Util viewWithText:title 
                                          font:[UIFont stampedBoldFontWithSize:12] 
                                         color:[UIColor whiteColor] 
                                          mode:UILineBreakModeClip 
                                    andMaxSize:CGSizeMake(200, 20)];
        titleView.frame = CGRectOffset(titleView.frame, height, titleOffsetY);
        [self addSubview:titleView];
        
        if (subtitle != nil) {
            UIView* subtitleView = [Util viewWithText:subtitle
                                                 font:[UIFont stampedFontWithSize:12]
                                                color:[UIColor stampedGrayColor]
                                                 mode:UILineBreakModeTailTruncation
                                           andMaxSize:CGSizeMake(200, 20)];
            [Util reframeView:subtitleView withDeltas:CGRectMake(height, CGRectGetMaxY(titleView.frame), 0, 0)];
            [self addSubview:subtitleView];
        }
    }
    return self;
}

- (void)setImage:(UIImage *)image {
    _imageView.image = image;
}

- (UIImage *)image {
    return _imageView.image;
}

- (void)dealloc
{
    [_imageView release];
    //NSLog(@"dealloc Confirmation");
    [super dealloc];
}

- (void)dismissed:(id)button {
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
}

+ (void)displayConfirmationWithTitle:(NSString*)title subtitle:(NSString*)subtitle andIconImage:(UIImage*)image {
    dispatch_async(dispatch_get_main_queue(), ^{
        @autoreleasepool {
            UIView* view = [[[STConfirmationView alloc] initWithTille:title subtitle:subtitle andIconImage:image] autorelease];
            view.frame = [Util centeredAndBounded:view.frame.size inFrame:[UIApplication sharedApplication].keyWindow.frame];
            [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor clearColor]];
            //[view release];
        }
    });
}

@end
