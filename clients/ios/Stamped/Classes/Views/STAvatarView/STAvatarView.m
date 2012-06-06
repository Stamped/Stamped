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
@synthesize backgroundView=_background;

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
        [self addSubview:imageView];
        _imageView = [imageView retain];
        [imageView release];
        
    }
    return self;
}

- (void)dealloc {
    [_background release], _background=nil;
    [_imageView release], _imageView=nil;
    [_imageURL release], _imageURL=nil;
    [super dealloc];
}

- (void)setDefault {
    
    self.imageView.image = [UIImage imageNamed:@"st_default_avatar.png"];
    
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return;
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
        
    self.imageView.image = nil;
    [[ImageLoader sharedLoader] imageForURL:_imageURL style:^UIImage*(UIImage *image){
      
        UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0);
        [image drawInRect:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
        UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
        return scaledImage;
        
    } styleIdentifier:@"st_avatar" completion:^(UIImage *image, NSURL *url) {
        if ([_imageURL isEqual:url]) {
            self.imageView.image = image;
        }
    }];
    
}

@end
