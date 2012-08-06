//
//  STAvatarView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "STAvatarView.h"
#import "ImageLoader.h"
#import "STTextCalloutView.h"
#import "STImageCache.h"

@implementation STAvatarView
@synthesize imageURL=_imageURL;
@synthesize imageView=_imageView;
@synthesize backgroundView=_background;
@synthesize delegate;
@synthesize calloutTitle;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.userInteractionEnabled = YES;
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectInset(self.bounds, 2.0f, 2.0f)];
        background.userInteractionEnabled = NO;
        background.backgroundColor = [UIColor whiteColor];
        background.layer.shadowPath = [UIBezierPath bezierPathWithRect:background.bounds].CGPath;
        background.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        background.layer.shadowRadius = 1.0f;
        background.layer.shadowOpacity = 0.2f;
        background.layer.rasterizationScale = [[UIScreen mainScreen] scale];
        background.layer.shouldRasterize = YES;
        [self addSubview:background];
        _background = [background retain];
        [background release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectInset(self.bounds, 3.0f, 3.0f)];
        imageView.backgroundColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        imageView.contentMode = UIViewContentModeScaleAspectFit;
        [self addSubview:imageView];
        _imageView = [imageView retain];
        [imageView release];
        
        [self addTarget:self action:@selector(viewSelected:) forControlEvents:UIControlEventTouchUpInside];
        
        UILongPressGestureRecognizer *gesture = [[UILongPressGestureRecognizer alloc] initWithTarget:self action:@selector(longPress:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        gesture.minimumPressDuration = 0.5f;
        [self addGestureRecognizer:gesture];
        [gesture release];
        
    }
    return self;
}

- (void)dealloc {
    [_background release], _background=nil;
    [_imageView release], _imageView=nil;
    [_imageURL release], _imageURL=nil;
    self.calloutTitle = nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setDefault {
    
    self.imageView.image = [UIImage imageNamed:@"st_default_avatar.png"];
    
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return;
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
    
    self.imageView.image = nil;
    [[STImageCache sharedInstance] imageForImageURL:imageURL.absoluteString andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
        UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0);
        [image drawInRect:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
        UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
        if ([_imageURL isEqual:imageURL]) {
            self.imageView.image = scaledImage;
        }
    }];
    //    [[ImageLoader sharedLoader] imageForURL:_imageURL style:^UIImage*(UIImage *image){
    //      
    //        UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0);
    //        [image drawInRect:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
    //        UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
    //        UIGraphicsEndImageContext();
    //        return scaledImage;
    //        
    //    } styleIdentifier:[NSString stringWithFormat:@"st_ava_%f", floorf(self.bounds.size.width)] completion:^(UIImage *image, NSURL *url) {
    //        if ([_imageURL isEqual:url]) {
    //            self.imageView.image = image;
    //        }
    //    }];
    
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    
    if (highlighted) {
        
        if (!highlightView) {
            UIView *view = [[UIView alloc] initWithFrame:_imageView.frame];
            view.backgroundColor = [UIColor blackColor];
            view.layer.masksToBounds = YES;
            [view setAlpha: 0.5];
            [self addSubview:view];
            [view release];
            highlightView = view;
        }
        
    } else {
        
        if (highlightView) {
            BOOL _enabled = [UIView areAnimationsEnabled];
            [UIView setAnimationsEnabled:YES];
            [UIView animateWithDuration:0.25f animations:^{
                highlightView.alpha = 0.0f;
            } completion:^(BOOL finished) {
                [highlightView removeFromSuperview];
                highlightView = nil;
            }];
            [UIView setAnimationsEnabled:_enabled];
            
        }
        
    }
    
    
}


#pragma mark - Actions

- (void)viewSelected:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stAvatarViewTapped:)]) {
        [self.delegate stAvatarViewTapped:self];
    }
    
}

- (void)longPress:(UILongPressGestureRecognizer*)gesture {
    
    if (!_calloutView) {
        STTextCalloutView *view = [[STTextCalloutView alloc] init];
        [self.superview addSubview:view];
        [view setTitle:self.calloutTitle boldText:self.calloutTitle];
        CGPoint pos = self.layer.position;
        [view showFromPosition:pos animated:YES];
    }
    
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    return (self.calloutTitle!=nil);
    
}


@end
