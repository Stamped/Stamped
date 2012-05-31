//
//  SocialSignupHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SocialSignupHeaderView.h"
#import "STAvatarView.h"

@implementation SocialSignupHeaderView

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
    
        STAvatarView *imageView = [[STAvatarView alloc] initWithFrame:CGRectMake(15.0f, 12.0f, 78.0f, 78.0f)];
        imageView.imageView.frame = CGRectInset(imageView.bounds, 4.0f, 4.0f);
        [self addSubview:imageView];
        _userImageView = imageView;
        [imageView release];
        
        UIImageView *stampView = [[UIImageView alloc] initWithFrame:CGRectMake(imageView.bounds.size.width-20, -8, 28.0f, 28.0f)];
        [imageView addSubview:stampView];
        _stampView = stampView;
        [stampView release];
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    
    
}

- (void)setStampColors:(NSArray*)colors {
    if (!colors || [colors count] < 2) return; // invalid colors
    
    UIGraphicsBeginImageContextWithOptions(_stampView.bounds.size, NO, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    
    CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
    CGContextScaleCTM(ctx, 1.0f, -1.0f);
    
    CGContextClipToMask(ctx, rect, [UIImage imageNamed:@"stamp_28pt_texture.png"].CGImage);
    drawStampGradient([[colors objectAtIndex:0] CGColor], [[colors objectAtIndex:1] CGColor], ctx);
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    _stampView.image = image;
    
}

@end
