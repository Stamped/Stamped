//
//  FilmDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/10/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "FilmDetailViewController.h"

@implementation FilmDetailViewController

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width,
                                           self.view.bounds.size.height + 60);
}

- (void)viewDidUnload {
  [super viewDidUnload];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
      [NSURL URLWithString:@"http://www.fandango.com/xmen:firstclass_133869/movieoverview"]];
}

@end
