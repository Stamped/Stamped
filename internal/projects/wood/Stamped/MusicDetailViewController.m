//
//  MusicDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/10/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "MusicDetailViewController.h"

@implementation MusicDetailViewController

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
}

- (void)viewDidUnload {
  [super viewDidUnload];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
      [NSURL URLWithString:@"itms://itunes.apple.com/us/album/wolfgang-amadeus-phoenix/id315002203"]];
}

@end
