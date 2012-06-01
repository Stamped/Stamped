//
//  STAvatarView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "STAvatarView.h"
#import "ImageLoader.h"

@implementation STAvatarView
@synthesize imageURL=_imageURL;
@synthesize imageView=_imageView;

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
        [background release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectInset(self.bounds, 3.0f, 3.0f)];
        imageView.backgroundColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:imageView];
        self.imageView = imageView;
        [imageView release];
        
    }
    return self;
}

- (void)dealloc {
    [_imageView release], _imageView=nil;
    [_imageURL release], _imageURL=nil;
    [super dealloc];
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return;
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
        
    self.imageView.image = nil;
    [[ImageLoader sharedLoader] imageForURL:_imageURL completion:^(UIImage *image, NSURL *url) {
        if ([_imageURL isEqual:url]) {
            self.imageView.image = image;
        }
    }];
    
}

@end
