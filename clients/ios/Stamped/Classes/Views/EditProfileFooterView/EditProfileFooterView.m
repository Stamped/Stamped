//
//  EditProfileFooterView.m
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import "EditProfileFooterView.h"

@implementation EditProfileFooterView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

        UIView *border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 1.0f)];
        border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        border.backgroundColor = [[UIColor blackColor] colorWithAlphaComponent:0.05f];
        [self addSubview:border];
        [border release];
        
        border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, self.bounds.size.width, 1.0f)];
        border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        border.backgroundColor = [[UIColor whiteColor] colorWithAlphaComponent:0.6f];
        [self addSubview:border];
        [border release];
        
        UIImage *image = [UIImage imageNamed:@"delete_btn_bg.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        button.titleLabel.font = [UIFont boldSystemFontOfSize:14];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        button.frame = CGRectMake(10.0f, 10.0f, self.bounds.size.width-20.0f, image.size.height);
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.2f] forState:UIControlStateNormal];
        [button setTitle:NSLocalizedString(@"Delete Account", @"Delete Account") forState:UIControlStateNormal];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        
    }
    return self;
}

#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(editProfileFooterViewDeleteAccount:)]) {
        [self.delegate editProfileFooterViewDeleteAccount:self];
    }
    
}


@end
