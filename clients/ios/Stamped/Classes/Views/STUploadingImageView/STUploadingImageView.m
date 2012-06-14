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
