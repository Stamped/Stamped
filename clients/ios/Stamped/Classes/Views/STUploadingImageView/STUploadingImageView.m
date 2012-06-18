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
@synthesize activiyView=_activiyView;
@synthesize deleteButton = _deleteButton;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.userInteractionEnabled = YES;
        
        UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        [self addSubview:view];
        self.activiyView = view;
        [view release];
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.imageEdgeInsets = UIEdgeInsetsMake(0, 16, 16, 0);
        [button setImage:[UIImage imageNamed:@"delete_icon.png"] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(delete:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        _deleteButton = button;
        
        CGRect frame = view.frame;
        frame.origin.x = (self.bounds.size.width-frame.size.width)/2;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        view.frame = frame;
        
    }
    return self;
}

- (void)dealloc {
    [_deleteButton release], _deleteButton = nil;
    self.activiyView = nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setImage:(UIImage *)image {
    [super setImage:image];
    
    self.hidden = (image==nil);
    _deleteButton.hidden = self.hidden;
    if (!image) return;
    
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
    
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
    self.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    self.layer.shadowRadius = 1.0f;
    self.layer.shadowOpacity = (image==nil) ? 0.0f : 0.2f;
    
    if (_deleteButton.superview == self) {
        [self.superview addSubview:_deleteButton];
    }
    _deleteButton.frame = CGRectMake(floorf(CGRectGetMaxX(self.frame)-34.0f), floorf(CGRectGetMinY(self.frame)-10.0f), 44.0f, 44.0f);
    
}

- (void)setUploading:(BOOL)uploading {
    _uploading = uploading;
    
    if (_uploading) {
        [self.activiyView startAnimating];
    } else {
        [self.activiyView stopAnimating];
    }
    
}

- (void)setFrame:(CGRect)frame {
    [super setFrame:frame];
    
    if (_deleteButton) {
        _deleteButton.frame = CGRectMake(CGRectGetMaxX(frame)-34.0f, CGRectGetMinY(frame)-10.0f, 44.0f, 44.0f);
    }
    
}


#pragma mark - Actions

- (void)delete:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(sTUploadingImageViewTapped:)]) {
        [self.delegate sTUploadingImageViewTapped:self];
    }

}

@end
