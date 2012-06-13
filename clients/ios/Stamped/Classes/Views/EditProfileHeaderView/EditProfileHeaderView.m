//
//  EditProfileHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import "EditProfileHeaderView.h"
#import "STAvatarView.h"
#import "UserStampView.h"

@implementation EditProfileHeaderView
@synthesize imageView=_imageView;
@synthesize stampView=_stampView;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.font = [UIFont boldSystemFontOfSize:12];
        label.text = @"Profile";
        
        [label sizeToFit];
        CGRect frame = label.frame;
        frame.origin.x = 15.0f;
        frame.origin.y = 15.0f;
        label.frame = frame;
        [self addSubview:label];
        [label release];
    
        STAvatarView *imageView = [[STAvatarView alloc] initWithFrame:CGRectMake(11.0f, 40.0f, 106.0f, 106.0f)];
        imageView.userInteractionEnabled = NO;
        imageView.imageView.frame = CGRectInset(imageView.bounds, 4.0f, 4.0f);
        [self addSubview:imageView];
        _imageView = [imageView retain];
        [imageView release];
        [_imageView setDefault];
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectMake(imageView.bounds.size.width-24, -26.0f, 46.0f, 46.0f)];
        stampView.size = STStampImageSize46;
        [imageView addSubview:stampView];
        [stampView setupWithUser:[[STStampedAPI sharedInstance] currentUser]];
        _stampView = stampView;
        [stampView release];
        _stampView = [_stampView retain];
        
        UIImage *image = [UIImage imageNamed:@"round_btn_bg.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor colorWithWhite:0.349f alpha:1.0f] forState:UIControlStateNormal];
        [button setTitle:@"   Change Picture" forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"camera_icon_small.png"] forState:UIControlStateNormal];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        button.frame = CGRectMake(CGRectGetMaxX(_imageView.frame) + 20.0f, 50.0f, 175.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [self addSubview:button];
        [button addTarget:self action:@selector(changePicture:) forControlEvents:UIControlEventTouchUpInside];
        
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setTitleColor:[UIColor colorWithWhite:0.349f alpha:1.0f] forState:UIControlStateNormal];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitle:@"   Change Color" forState:UIControlStateNormal];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        button.frame = CGRectMake(CGRectGetMaxX(_imageView.frame) + 20.0f, 96.0f, 175.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [self addSubview:button];
        [button addTarget:self action:@selector(changeColor:) forControlEvents:UIControlEventTouchUpInside];
        _stampColorButton = button;
        
        image = [Util stampImageForUser:[[STStampedAPI sharedInstance] currentUser] withSize:STStampImageSize18];
        [button setImage:image forState:UIControlStateNormal];

        
    }
    return self;
}

- (void)dealloc {
    [_imageView release], _imageView=nil;
    [_stampView release], _stampView=nil;
    [super dealloc];
}


#pragma mark - Actions

- (void)changeColor:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(editProfileHeaderViewChangeColor:)]) {
        [self.delegate editProfileHeaderViewChangeColor:self];
    }
    
}

- (void)changePicture:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(editProfileHeaderViewChangePicture:)]) {
        [self.delegate editProfileHeaderViewChangePicture:self];
    }
    
}


#pragma mark - Setters

- (void)setStampColors:(NSArray*)colors {
    
    [self.stampView setupWithColors:colors];
    
    UIGraphicsBeginImageContextWithOptions(CGSizeMake(18.0f, 18.0f), NO, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);
    CGContextClipToMask(ctx, rect, [UIImage imageNamed:@"stamp_18pt_texture.png"].CGImage);
    CGGradientRef gradient = CGGradientCreateWithColors(NULL, (CFArrayRef)[NSArray arrayWithObjects:(id)[[colors objectAtIndex:0] CGColor],(id)[[colors objectAtIndex:1] CGColor], nil], NULL);
    CGPoint start = CGPointMake(rect.origin.x, rect.origin.y + rect.size.height);
    CGPoint end = CGPointMake(rect.origin.x + rect.size.width, rect.origin.y);
    CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradient);
    
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    [_stampColorButton setImage:image forState:UIControlStateNormal];
    
}


#pragma mark - Getters

- (NSArray*)colors {
    
    return [self.stampView colors];
    
}


@end
