//
//  STUploadingImageView.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "STUploadingImageView.h"
#import "STS3Uploader.h"

@implementation STUploadingImageView
@synthesize uploading=_uploading;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        [self addSubview:view];
        self.activiyView = view;
        [view release];
        
        CGRect frame = view.frame;
        frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        view.frame = frame;
        
    }
    return self;
}

- (void)setImage:(UIImage *)image {
    [super setImage:image];
    
    CGSize kMaxImageViewSize = CGSizeMake(200.0f, 200.0f);
    
    CGSize imageSize = image.size;
    CGFloat aspectRatio = imageSize.width / imageSize.height;
    CGRect frame = self.frame;
    if (kMaxImageViewSize.width / aspectRatio <= kMaxImageViewSize.height) {
        frame.size.width = kMaxImageViewSize.width;
        frame.size.height = frame.size.width / aspectRatio;
    } else {
        frame.size.height = kMaxImageViewSize.height;
        frame.size.width = frame.size.height * aspectRatio;
    }
    
    frame.origin.x = (self.superview.bounds.size.width-frame.size.width)/2;
    self.frame = frame;

    self.layer.borderColor = [UIColor whiteColor].CGColor;
    self.layer.borderWidth = 2.0f;
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    self.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    self.layer.shadowRadius = 1.0f;
    self.layer.shadowOpacity = (image==nil) ? 0.0f : 0.2f;
    
}

- (void)dealloc {
    self.activiyView = nil;
    [super dealloc];
}

- (void)setUploading:(BOOL)uploading {
    _uploading = uploading;
    
    if (_uploading) {
        [self.activiyView startAnimating];
    } else {
        [self.activiyView stopAnimating];
    }
    
}


@end
